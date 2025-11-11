from flask import jsonify, request

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
