from flask import current_app, jsonify, redirect, request, url_for

from app.modules.fakenodo import fakenodo_bp
from app.modules.fakenodo.services import FakenodoService

service = FakenodoService()


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


@fakenodo_bp.route('/fakenodo/deposit/depositions/<int:deposition_id>/versions', methods=['GET'], endpoint='list_versions')
def listar_versiones(deposition_id):
    versions = service.list_versions(deposition_id)
    return jsonify({'versions': versions}), 200


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