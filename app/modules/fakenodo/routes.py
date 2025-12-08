from flask import current_app, flash, jsonify, redirect, render_template, request, url_for

from app.modules.fakenodo import fakenodo_bp
from app.modules.fakenodo.services import FakenodoService

service = FakenodoService()


@fakenodo_bp.route('/fakenodo', methods=['GET'], endpoint='index')
def fakenodo_index():
    """Render the Fakenodo index page with API documentation."""
    return render_template('fakenodo/index.html')


@fakenodo_bp.route('/fakenodo/deposit/depositions', methods=['POST'], endpoint='create_deposition')
def crear_deposito():
    payload = request.get_json(silent=True) or {}
    metadata = payload.get('metadata') if isinstance(payload, dict) else {}
    rec = service.create_deposition(metadata=metadata)
    return jsonify(rec), 201


@fakenodo_bp.route('/fakenodo/deposit/depositions', methods=['GET'], endpoint='get_all_depositions')
def listar_depositos():
    records = service.list_depositions()
    return jsonify({'depositions': records}), 200


@fakenodo_bp.route('/fakenodo/deposit/depositions/<int:deposition_id>', methods=['GET'], endpoint='get_deposition')
def obtener_deposito(deposition_id):
    rec = service.get_deposition(deposition_id)
    if not rec:
        return jsonify({'message': 'Depósito no encontrado'}), 404
    return jsonify(rec), 200


@fakenodo_bp.route('/fakenodo/deposit/depositions/<int:deposition_id>', methods=['DELETE'], endpoint='delete_deposition')
def eliminar_deposito(deposition_id):
    ok = service.delete_deposition(deposition_id)
    if not ok:
        return jsonify({'message': 'Depósito no encontrado'}), 404
    return jsonify({'status': 'success', 'id': deposition_id}), 200


@fakenodo_bp.route('/fakenodo/deposit/depositions/<int:deposition_id>/files', methods=['POST'], endpoint='upload_file')
def subir_fichero(deposition_id):
    uploaded = request.files.get('file')
    name = request.form.get('name') or (uploaded.filename if uploaded else None)
    content = uploaded.read() if uploaded else None

    if not name:
        return jsonify({'message': 'Nombre de fichero no proporcionado'}), 400

    file_record = service.upload_file(deposition_id, name, content)
    if not file_record:
        return jsonify({'message': 'Depósito no encontrado'}), 404
    return jsonify(file_record), 201


@fakenodo_bp.route('/fakenodo/deposit/depositions/<int:deposition_id>/actions/publish', methods=['POST'], endpoint='publish_deposition')
def publicar_deposito(deposition_id):
    version = service.publish_deposition(deposition_id)
    if not version:
        return jsonify({'message': 'Depósito no encontrado'}), 404
    return jsonify(version), 202

@fakenodo_bp.route('/fakenodo/deposit/depositions/<int:deposition_id>/metadata', methods=['PATCH'], endpoint='update_deposition_metadata')
def actualizar_metadata(deposition_id):
    """Actualizar solo la metadata de una deposition sin generar nueva versión.

    Enviar JSON: {"metadata": {...}}. No devuelve nuevo DOI.
    """
    payload = request.get_json(silent=True) or {}
    if 'metadata' in payload and isinstance(payload['metadata'], dict):
        metadata = payload['metadata']
    else:
        metadata = {k: v for k, v in payload.items() if k in ['title', 'description', 'tags', 'publication_type', 'publication_doi']}

    tags_val = metadata.get('tags')
    if isinstance(tags_val, list):
        metadata['tags'] = ','.join(t.strip() for t in tags_val if t and isinstance(t, str))

    updated = service.update_metadata(deposition_id, metadata)
    if not updated:
        return jsonify({'message': 'Depósito no encontrado'}), 404
    try:
        from app import db
        from app.modules.dataset.models import DSMetaData
        dsmeta = DSMetaData.query.filter_by(deposition_id=deposition_id).first()
        if dsmeta:
            changed = False
            for field in ['title', 'description', 'tags']:
                if field in metadata and getattr(dsmeta, field) != metadata[field]:
                    setattr(dsmeta, field, metadata[field])
                    changed = True
            if changed:
                db.session.add(dsmeta)
                db.session.commit()
    except Exception as sync_exc:
        current_app.logger.warning('No se pudo sincronizar metadata de deposition %s al dataset: %s', deposition_id, sync_exc)

    return jsonify({'id': deposition_id, 'metadata': updated.get('metadata'), 'dirty': updated.get('dirty'), 'versions': updated.get('versions')}), 200


@fakenodo_bp.route('/fakenodo/deposit/depositions/<int:deposition_id>/versions', methods=['GET'], endpoint='list_versions')
def listar_versiones(deposition_id):
    dep = service.get_deposition(deposition_id)
    if not dep:
        return jsonify({'message': 'Depósito no encontrado', 'versions': []}), 404
    
    versions = service.list_versions(deposition_id)
    return jsonify({'versions': versions or []}), 200


@fakenodo_bp.route('/fakenodo/test', methods=['GET'], endpoint='test_endpoint')
def prueba_endpoint():
    return service.test_full_connection()



@fakenodo_bp.route('/dataset/<int:dataset_id>/sync', methods=['GET', 'POST'], endpoint='dataset_sync_proxy')
def dataset_sync_proxy(deposition_id=None, dataset_id=None):
    from app.modules.dataset import routes as dataset_routes

    if request.method == 'GET':
        return redirect(url_for('dataset.get_unsynchronized_dataset', dataset_id=dataset_id))

    view_fn = current_app.view_functions.get("dataset.sync_dataset")
    if view_fn:
        return view_fn(dataset_id)

    try:
       
        import importlib

        mod = importlib.import_module("app.modules.dataset.routes")
        fn = getattr(mod, "sync_dataset", None)
        if fn:
            return fn(dataset_id)

       
        current_app.logger.warning(
            "dataset.sync_dataset not available in module app.modules.dataset.routes; attempting direct service fallback"
        )

        ds_service = getattr(mod, "dataset_service", None)
        zen_service = getattr(mod, "zenodo_service", None)
        if not ds_service or not zen_service:
            current_app.logger.error("Required services not available on dataset module: dataset_service=%s zenodo_service=%s", ds_service, zen_service)
            return (jsonify({"message": "Sync handler not available"}), 500)

        try:
            ds_any = ds_service.repository.get_by_id(dataset_id)
            if not ds_any:
                from flask import flash

                flash("Dataset no encontrado.", "warning")
                return redirect(url_for("dataset.list_dataset"))

            from flask_login import current_user

            if not (current_user and current_user.is_authenticated and ds_any.user_id == current_user.id):
                from flask import flash

                flash("No tienes permiso para publicar este dataset.", "danger")
                return redirect(url_for("dataset.list_dataset"))

            existing_doi = getattr(getattr(ds_any, "ds_meta_data", None), "dataset_doi", None)
            if existing_doi:
                from flask import flash

                flash("Este dataset ya está publicado en el repositorio remoto.", "info")
                return redirect(url_for("dataset.list_dataset"))

            dataset = ds_any

            resp = zen_service.create_new_deposition(dataset)
            deposition_id = resp.get("id") if resp else None
            if not deposition_id:
                from flask import flash

                flash("No se pudo crear la deposition en el repositorio remoto.", "danger")
                return redirect(url_for("dataset.get_unsynchronized_dataset", dataset_id=dataset.id))

            ds_service.update_dsmetadata(dataset.ds_meta_data_id, deposition_id=deposition_id)

            for fm in getattr(dataset, "feature_models", []) + getattr(dataset, "file_models", []):
                try:
                    zen_service.upload_file(dataset, deposition_id, fm)
                except Exception:
                    current_app.logger.exception("Error subiendo fichero para dataset %s fm=%s", getattr(dataset, 'id', '?'), getattr(fm, 'id', '?'))

            zen_service.publish_deposition(deposition_id)
            doi = zen_service.get_doi(deposition_id)
            ds_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_doi=doi)

        except Exception as exc:
            current_app.logger.exception("Error during fallback sync for dataset %s: %s", dataset_id, exc)
            from flask import flash

            flash(f"Error sincronizando dataset: {exc}", "danger")
            return redirect(url_for("dataset.get_unsynchronized_dataset", dataset_id=dataset_id))
    except Exception as exc:
        current_app.logger.exception("Error calling dataset.sync_dataset fallback: %s", exc)
        return (jsonify({"message": "Internal error while trying to sync dataset"}), 500)


@fakenodo_bp.route('/fakenodo/dataset/<int:dataset_id>/create', methods=['POST'], endpoint='create_dataset_deposition')
def create_dataset_deposition(dataset_id: int):
    """Crear solo el registro (deposition) preliminar para un dataset.
    """
    try:
        from flask_login import current_user

        from app.modules.dataset.services import DataSetService

        ds_service = DataSetService()
        ds_any = ds_service.repository.get_by_id(dataset_id)
        if not ds_any:
            flash('Dataset no encontrado.', 'warning')
            return redirect(url_for('dataset.list_dataset'))

        if not (current_user and current_user.is_authenticated and ds_any.user_id == current_user.id):
            flash('No tienes permiso para modificar este dataset.', 'danger')
            return redirect(url_for('dataset.list_dataset'))

        meta = getattr(ds_any, 'ds_meta_data', None)
        if not meta:
            flash('Metadatos del dataset no disponibles.', 'danger')
            return redirect(url_for('dataset.list_dataset'))

        if getattr(meta, 'dataset_doi', None):
            flash('El dataset ya está publicado.', 'info')
            return redirect(url_for('dataset.list_dataset'))

        if getattr(meta, 'deposition_id', None):
            flash('El dataset ya tiene un registro preliminar creado.', 'info')
            return redirect(url_for('dataset.get_unsynchronized_dataset', dataset_id=dataset_id))

        resp = service.create_deposition(metadata={'title': meta.title})
        deposition_id = resp.get('id') if resp else None
        if not deposition_id:
            flash('No se pudo crear el registro remoto.', 'danger')
            return redirect(url_for('dataset.get_unsynchronized_dataset', dataset_id=dataset_id))

        ds_service.update_dsmetadata(ds_any.ds_meta_data_id, deposition_id=deposition_id)
        ds_service.update_version_doi(dataset_id)
        flash('Registro preliminar creado correctamente. Ahora puedes publicarlo.', 'success')
        return redirect(url_for('dataset.get_unsynchronized_dataset', dataset_id=dataset_id))
    except Exception as exc:
        current_app.logger.exception('Error creando deposition preliminar para dataset %s: %s', dataset_id, exc)
        flash(f'Error creando el registro: {exc}', 'danger')
        return redirect(url_for('dataset.get_unsynchronized_dataset', dataset_id=dataset_id))


@fakenodo_bp.route('/fakenodo/dataset/<int:dataset_id>/publish', methods=['POST'], endpoint='publish_dataset_deposition')
def publish_dataset_deposition(dataset_id: int):
    """Publicar una deposition ya creada y actualizar DOI del dataset.
    """
    try:
        from flask_login import current_user

        from app.modules.dataset.services import DataSetService

        ds_service = DataSetService()
        ds_any = ds_service.repository.get_by_id(dataset_id)
        if not ds_any:
            flash('Dataset no encontrado.', 'warning')
            return redirect(url_for('dataset.list_dataset'))

        if not (current_user and current_user.is_authenticated and ds_any.user_id == current_user.id):
            flash('No tienes permiso para publicar este dataset.', 'danger')
            return redirect(url_for('dataset.list_dataset'))

        meta = getattr(ds_any, 'ds_meta_data', None)
        if not meta:
            flash('Metadatos del dataset no disponibles.', 'danger')
            return redirect(url_for('dataset.list_dataset'))

        if getattr(meta, 'dataset_doi', None):
            flash('Este dataset ya está publicado.', 'info')
            return redirect(url_for('dataset.list_dataset'))

        deposition_id = getattr(meta, 'deposition_id', None)
        if not deposition_id:
            flash('Primero debes crear el registro preliminar.', 'warning')
            return redirect(url_for('dataset.get_unsynchronized_dataset', dataset_id=dataset_id))

        for fm in getattr(ds_any, 'feature_models', []) + getattr(ds_any, 'file_models', []):
            try:
                service.upload_file(deposition_id, getattr(fm, 'filename', None) or getattr(fm, 'name', f'fm_{getattr(fm, "id", "?")}.bin'), None)
            except Exception:
                current_app.logger.exception('Error subiendo fichero para dataset %s fm=%s', ds_any.id, getattr(fm, 'id', '?'))

        version = service.publish_deposition(deposition_id)
        if not version:
            flash('No se pudo publicar la deposition.', 'danger')
            return redirect(url_for('dataset.get_unsynchronized_dataset', dataset_id=dataset_id))

        doi = service.get_doi(deposition_id)
        if doi:
            ds_service.update_dsmetadata(ds_any.ds_meta_data_id, dataset_doi=doi)
            flash(f'Dataset publicado correctamente. DOI: {doi}', 'success')
        else:
            flash('Publicación realizada pero no se obtuvo DOI.', 'warning')

        return redirect(url_for('dataset.list_dataset'))
    except Exception as exc:
        current_app.logger.exception('Error publicando deposition para dataset %s: %s', dataset_id, exc)
        flash(f'Error publicando dataset: {exc}', 'danger')
        return redirect(url_for('dataset.get_unsynchronized_dataset', dataset_id=dataset_id))