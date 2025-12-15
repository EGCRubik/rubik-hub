from flask import current_app, jsonify, redirect, render_template, request, url_for
from flask_login import current_user

from app import db
from app.modules.dataset.models import DSMetaData
from app.modules.dataset.services import DataSetService
from app.modules.fakenodo import fakenodo_bp
from app.modules.fakenodo.services import FakenodoService

service = FakenodoService()


@fakenodo_bp.route('/fakenodo', methods=['GET'], endpoint='index')
def fakenodo_index():
    return render_template('fakenodo/index.html')

@fakenodo_bp.route('/fakenodo/deposit/depositions', methods=['GET'], endpoint='get_all_depositions')
def list_depositions():
    return jsonify({'depositions': service.list_depositions()}), 200


@fakenodo_bp.route('/fakenodo/deposit/depositions/<int:deposition_id>', methods=['GET'], endpoint='get_deposition')
def get_deposition(deposition_id):
    rec = service.get_deposition(deposition_id)
    return (jsonify(rec), 200) if rec else (jsonify({'message': 'Depósito no encontrado'}), 404)


@fakenodo_bp.route('/fakenodo/deposit/depositions/<int:deposition_id>/files', methods=['POST'], endpoint='upload_file')
def upload_file(deposition_id):
    uploaded = request.files.get('file')
    name = request.form.get('name') or (uploaded.filename if uploaded else None)
    if not name:
        return jsonify({'message': 'Nombre de fichero no proporcionado'}), 400
    file_record = service.upload_file(deposition_id, name, uploaded.read() if uploaded else None)
    return (jsonify(file_record), 201) if file_record else (jsonify({'message': 'Depósito no encontrado'}), 404)


@fakenodo_bp.route('/fakenodo/deposit/depositions/<int:deposition_id>/metadata', methods=['PATCH'], endpoint='update_deposition_metadata')
def update_deposition_metadata(deposition_id):
    payload = request.get_json(silent=True) or {}
    metadata = payload.get('metadata') if 'metadata' in payload and isinstance(payload['metadata'], dict) else {k: v for k, v in payload.items() if k in ['title', 'description', 'tags', 'publication_type', 'publication_doi']}
    if isinstance(metadata.get('tags'), list):
        metadata['tags'] = ','.join(t.strip() for t in metadata['tags'] if t and isinstance(t, str))
    updated = service.update_metadata(deposition_id, metadata)
    if not updated:
        return jsonify({'message': 'Depósito no encontrado'}), 404
    dsmeta = DSMetaData.query.filter_by(deposition_id=deposition_id).first()
    if dsmeta:
        for field in ['title', 'description', 'tags']:
            if field in metadata and getattr(dsmeta, field) != metadata[field]:
                setattr(dsmeta, field, metadata[field])
        db.session.commit()
    return jsonify({'id': deposition_id, 'metadata': updated.get('metadata'), 'dirty': updated.get('dirty'), 'versions': updated.get('versions')}), 200


@fakenodo_bp.route('/fakenodo/deposit/depositions/<int:deposition_id>/versions', methods=['GET'], endpoint='list_versions')
def list_versions(deposition_id):
    dep = service.get_deposition(deposition_id)
    if not dep:
        return jsonify({'message': 'Depósito no encontrado', 'versions': []}), 404
    return jsonify({'versions': service.list_versions(deposition_id) or []}), 200


@fakenodo_bp.route('/fakenodo/test', methods=['GET'], endpoint='test_endpoint')
def test_endpoint():
    return service.test_full_connection()


@fakenodo_bp.route('/dataset/<int:dataset_id>/sync', methods=['GET', 'POST'], endpoint='dataset_sync_proxy')
def dataset_sync_proxy(dataset_id=None):
    if request.method == 'GET':
        return redirect(url_for('dataset.get_unsynchronized_dataset', dataset_id=dataset_id))
    view_fn = current_app.view_functions.get("dataset.sync_dataset")
    if view_fn:
        return view_fn(dataset_id)
    return jsonify({"message": "Sync handler not available"}), 500


@fakenodo_bp.route('/fakenodo/dataset/<int:dataset_id>/create', methods=['POST'], endpoint='create_dataset_deposition')
def create_dataset_deposition(dataset_id: int):
    ds_service = DataSetService()
    ds = ds_service.repository.get_by_id(dataset_id)
    meta = getattr(ds, 'ds_meta_data', None) if ds else None
    if not ds or not meta or not (current_user and current_user.is_authenticated and ds.user_id == current_user.id):
        return redirect(url_for('dataset.list_dataset'))
    if getattr(meta, 'dataset_doi', None) or getattr(meta, 'deposition_id', None):
        return redirect(url_for('dataset.list_dataset'))
    resp = service.create_deposition(metadata={'title': meta.title})
    deposition_id = resp.get('id') if resp else None
    if deposition_id:
        ds_service.update_dsmetadata(ds.ds_meta_data_id, deposition_id=deposition_id)
        ds_service.update_version_doi(dataset_id)
    return redirect(url_for('dataset.get_unsynchronized_dataset', dataset_id=dataset_id))


@fakenodo_bp.route('/fakenodo/dataset/<int:dataset_id>/publish', methods=['POST'], endpoint='publish_dataset_deposition')
def publish_dataset_deposition(dataset_id: int):
    ds_service = DataSetService()
    ds = ds_service.repository.get_by_id(dataset_id)
    meta = getattr(ds, 'ds_meta_data', None) if ds else None
    if not ds or not meta or not (current_user and current_user.is_authenticated and ds.user_id == current_user.id):
        return redirect(url_for('dataset.list_dataset'))
    if getattr(meta, 'dataset_doi', None):
        return redirect(url_for('dataset.list_dataset'))
    deposition_id = getattr(meta, 'deposition_id', None)
    if not deposition_id:
        return redirect(url_for('dataset.get_unsynchronized_dataset', dataset_id=dataset_id))
    for fm in getattr(ds, 'feature_models', []) + getattr(ds, 'file_models', []):
        service.upload_file(deposition_id, getattr(fm, 'filename', None) or getattr(fm, 'name', f'fm_{getattr(fm, "id", "?")}.bin'), None)
    version = service.publish_deposition(deposition_id)
    if version:
        doi = service.get_doi(deposition_id)
        ds_service.update_dsmetadata(ds.ds_meta_data_id, dataset_doi=doi)
    return redirect(url_for('dataset.list_dataset'))

# He utilizado parcialmente la inteligencia artificial (IA) como herramienta de apoyo durante el desarrollo y modificación de este archivo de código. 
# La IA me ha ayudado a entender, optimizar y automatizar ciertas tareas, pero la implementación final y las decisiones clave han sido realizadas por mí.
