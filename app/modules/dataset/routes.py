import json
import logging
import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from typing import Optional
from zipfile import ZipFile

import requests
from flask import abort, flash, jsonify, make_response, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.modules.dataset import dataset_bp
from app.modules.dataset.forms import DataSetForm
from app.modules.dataset.models import DSDownloadRecord
from app.modules.dataset.services import (
    AuthorService,
    DataSetService,
    DOIMappingService,
    DSDownloadRecordService,
    DSMetaDataService,
    DSViewRecordService,
)
from app.utils import notifications
from app.utils.notifications import notify_followers_of_author

logger = logging.getLogger(__name__)


dataset_service = DataSetService()
author_service = AuthorService()
dsmetadata_service = DSMetaDataService()


class FakenodoAdapter:
    """Adapter that routes dataset operations either to a remote FakeNODO HTTP API
    (when FAKENODO_URL env var is set to an http URL) or to the local DB-backed
    FakenodoService (lazy-imported to avoid touching the DB at module import).
    """

    def __init__(self, working_dir: str | None = None):
        self.base_url = os.getenv("FAKENODO_URL")
        self.working_dir = working_dir
        self._service = None
        self.is_remote = bool(self.base_url and str(self.base_url).startswith("http"))

    def _get_service(self):
        if not self._service:
            # lazy import to avoid DB access at import-time
            from app.modules.fakenodo.services import FakenodoService

            self._service = FakenodoService()
        return self._service

    def create_new_deposition(self, dataset) -> dict:
        metadata = {
            "title": getattr(dataset, "title", f"dataset-{getattr(dataset, 'id', '')}"),
        }
        if self.is_remote:
            url = f"{self.base_url.rstrip('/')}/deposit/depositions"
            try:
                resp = requests.post(url, json={"metadata": metadata}, timeout=10)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                raise
        else:
            svc = self._get_service()
            return svc.create_new_deposition(metadata=metadata)

    def upload_file(self, dataset, deposition_id, feature_model) -> Optional[dict]:
        name = getattr(feature_model, "filename", None) or getattr(feature_model, "name", None)
        path = getattr(feature_model, "file_path", None) or getattr(feature_model, "path", None)
        content = None
        try:
            if path and os.path.exists(path):
                with open(path, "rb") as fh:
                    content = fh.read()
        except Exception:
            content = None

        if not name:
            name = f"feature_model_{getattr(feature_model, 'id', uuid.uuid4())}.bin"

        if self.is_remote:
            url = f"{self.base_url.rstrip('/')}/deposit/depositions/{deposition_id}/files"
            files = {"file": (name, content)}
            data = {"name": name}
            try:
                resp = requests.post(url, files=files, data=data, timeout=30)
                resp.raise_for_status()
                return resp.json()
            except Exception:
                raise
        else:
            svc = self._get_service()
            return svc.upload_file(deposition_id, name, content)
        notifications.notify_followers_of_author(dataset)

    def publish_deposition(self, deposition_id):
        if self.is_remote:
            url = f"{self.base_url.rstrip('/')}/deposit/depositions/{deposition_id}/actions/publish"
            resp = requests.post(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        else:
            svc = self._get_service()
            return svc.publish_deposition(deposition_id)

    def get_doi(self, deposition_id):
        if self.is_remote:
            url = f"{self.base_url.rstrip('/')}/deposit/depositions/{deposition_id}"
            resp = requests.get(url, timeout=10)
            if not resp.ok:
                return None
            rec = resp.json()
            doi = rec.get("doi")
            if doi:
                return doi
            versions = rec.get("versions") or []
            if versions:
                return versions[-1].get("doi")
            return None
        else:
            svc = self._get_service()
            return svc.get_doi(deposition_id)


zenodo_service = FakenodoAdapter(working_dir=os.getenv("WORKING_DIR"))
doi_mapping_service = DOIMappingService()
ds_view_record_service = DSViewRecordService()


@dataset_bp.route("/dataset/upload", methods=["GET", "POST"])
@login_required
def create_dataset():
    form = DataSetForm()

    if request.method == "POST":
        valid = form.validate_on_submit()
        if not valid:
            # Ignoramos errores de file_models en este primer paso
            other_errors = {k: v for k, v in form.errors.items() if k != "file_models"}
            if other_errors:
                logger.debug("create_dataset validation failed with errors: %s", other_errors)
                return render_template("dataset/upload_dataset.html", form=form, messages=form.errors)

        # Si el formulario básico es válido, pasamos al paso tabular
        return render_template("dataset/upload_tabular.html", form=form)

    return render_template("dataset/upload_dataset.html", form=form)


@dataset_bp.route("/dataset/upload/uvl", methods=["GET", "POST"])
@login_required
def create_uvl_dataset():
    form = DataSetForm()

    if request.method == "GET":
        return render_template("dataset/upload_uvl.html", form=form)

    if not form.validate_on_submit():
        return jsonify({"message": form.errors}), 400

    dataset = None

    try:
        logger.info("Creating dataset...")
        dataset = dataset_service.create_from_form(form=form, current_user=current_user)
        logger.info(f"Created dataset: {dataset}")
        dataset_service.move_feature_models(dataset)
    except Exception as exc:
        logger.exception(f"Exception while create dataset data in local {exc}")
        return jsonify({"Exception while create dataset data in local: ": str(exc)}), 400

    data = {}
    try:
        zenodo_response_json = zenodo_service.create_new_deposition(dataset)
        response_data = json.dumps(zenodo_response_json)
        data = json.loads(response_data)
    except Exception as exc:
        data = {}
        zenodo_response_json = {}
        logger.exception(f"Exception while create dataset data in Zenodo {exc}")

    if data.get("conceptrecid"):
        deposition_id = data.get("id")

        dataset_service.update_dsmetadata(dataset.ds_meta_data_id, deposition_id=deposition_id)

        try:
            for feature_model in dataset.feature_models:
                zenodo_service.upload_file(dataset, deposition_id, feature_model)

            zenodo_service.publish_deposition(deposition_id)
            deposition_doi = zenodo_service.get_doi(deposition_id)
            dataset_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_doi=deposition_doi)
        except Exception as e:
            msg = f"it has not been possible upload feature models in Zenodo and update the DOI: {e}"
            return jsonify({"message": msg}), 200

    file_path = current_user.temp_folder()
    if os.path.exists(file_path) and os.path.isdir(file_path):
        shutil.rmtree(file_path)

    msg = "Everything works!"
    return jsonify({"message": msg}), 200


@dataset_bp.route("/dataset/upload/csv", methods=["GET", "POST"])
@login_required
def upload_csv():
    form = DataSetForm()

    if request.method == "GET":
        # Render del paso tabular (metadatos + fichero CSV)
        return render_template("dataset/upload_tabular.html", form=form)

    # POST: procesamos la solicitud cuando el usuario envía el formulario con un archivo CSV.
    # 1) Obtenemos el archivo CSV de la solicitud.
    csv_file = request.files.get("csv_file")
    if csv_file is None or csv_file.filename == "":
        return jsonify({"message": "No CSV file uploaded"}), 400

    filename = secure_filename(csv_file.filename)
    if not filename.lower().endswith(".csv"):
        return jsonify({"message": "Please upload a .csv file"}), 400

    # 2) Guardamos el archivo en una carpeta temporal del usuario.
    temp_folder = current_user.temp_folder()
    os.makedirs(temp_folder, exist_ok=True)

    dest_path = os.path.join(temp_folder, filename)
    if os.path.exists(dest_path):
        base, ext = os.path.splitext(filename)
        i = 1
        while os.path.exists(os.path.join(temp_folder, f"{base} ({i}){ext}")):
            i += 1
        filename = f"{base} ({i}){ext}"
        dest_path = os.path.join(temp_folder, filename)

    try:
        csv_file.save(dest_path)
    except Exception as exc:
        return jsonify({"message": f"Could not save uploaded file: {exc}"}), 500

    # 3) Rellenamos los campos del formulario con los datos del POST
    form.title.data = request.form.get("title")
    form.desc.data = request.form.get("desc")
    form.publication_type.data = request.form.get("publication_type")
    form.publication_doi.data = request.form.get("publication_doi")
    form.dataset_doi.data = request.form.get("dataset_doi")
    form.tags.data = request.form.get("tags")

    # 4) Aseguramos que haya al menos una entrada en "file_models" y asignamos el nombre del CSV.
    try:
        if len(form.file_models.entries) == 0:
            entry = form.file_models.append_entry()
        else:
            entry = form.file_models.entries[0]
        entry_form = getattr(entry, "form", entry)
        entry_form.csv_filename.data = filename
    except Exception as exc:
        logger.exception("Error preparing file_models entry: %s", exc)
        return jsonify({"message": "Internal error building form data"}), 500

    # 5) Validamos el formulario completo (incluyendo file_models)
    if not form.validate():
        logger.debug("upload_csv validation failed: %s", form.errors)
        return jsonify({"message": form.errors}), 400

    # 6) Creamos el dataset en la base de datos y movemos el archivo al directorio final.
    try:
        logger.info("Creating dataset...")
        dataset = dataset_service.create_from_form(form=form, current_user=current_user)
        logger.info(f"Created dataset with ID: {dataset.id} and title: {dataset.ds_meta_data.title}")
        dataset_service.move_file_models(dataset)
    except Exception as exc:
        logger.exception(f"Error creating dataset: {exc}")
        return jsonify({"message": str(exc)}), 500
    
    # send dataset as deposition to Fakenodo
    data = {}
    try:
        fakenodo_response_json = zenodo_service.create_new_deposition(dataset)
        response_data = json.dumps(fakenodo_response_json)
        data = json.loads(response_data)
    except Exception as exc:
        data = {}
        fakenodo_response_json = {}
        logger.exception(f"Exception while create dataset data in Fakenodo {exc}")

    if data.get("conceptrecid"):
        deposition_id = data.get("id")

        # update dataset with deposition id in Fakenodo
        dataset_service.update_dsmetadata(dataset.ds_meta_data_id, deposition_id=deposition_id)

        try:
            # iterate for each file model (one file model = one request to Fakenodo)
            for file_model in dataset.file_models:
                zenodo_service.upload_file(dataset, deposition_id, file_model)

            # publish deposition
            zenodo_service.publish_deposition(deposition_id)

            # update DOI
            deposition_doi = zenodo_service.get_doi(deposition_id)
            dataset_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_doi=deposition_doi)
        except Exception as e:
            msg = f"it has not been possible upload feature models in Fakenodo and update the DOI: {e}"
            return jsonify({"message": msg}), 200

    # Finalmente, redirigimos al usuario a la lista de datasets.
    return redirect(url_for("dataset.list_dataset"))


@dataset_bp.route("/dataset/list", methods=["GET", "POST"])
@login_required
def list_dataset():
    return render_template(
        "dataset/list_datasets.html",
        datasets=dataset_service.get_synchronized(current_user.id),
        local_datasets=dataset_service.get_unsynchronized(current_user.id),
    )


@dataset_bp.route("/dataset/file/upload", methods=["POST"])
@login_required
def upload():
    # Save uploaded CSV to user's temp folder (Backward-compatible endpoint).
    file = request.files.get("csv_file")
    temp_folder = current_user.temp_folder()

    if file is None or not file.filename or not file.filename.lower().endswith(".csv"):
        return jsonify({"message": "No valid file"}), 400

    os.makedirs(temp_folder, exist_ok=True)

    # ensure unique filename in temp folder
    file_path = os.path.join(temp_folder, file.filename)
    if os.path.exists(file_path):
        base_name, extension = os.path.splitext(file.filename)
        i = 1
        while os.path.exists(os.path.join(temp_folder, f"{base_name} ({i}){extension}")):
            i += 1
        new_filename = f"{base_name} ({i}){extension}"
        file_path = os.path.join(temp_folder, new_filename)
    else:
        new_filename = file.filename

    try:
        file.save(file_path)
    except Exception as e:
        logger.exception("Error saving uploaded file: %s", e)
        return jsonify({"message": str(e)}), 500

    # If the POST contains dataset fields (tabular multi-step flow), create the dataset now.
    # We check for presence of a title or explicit dataset_type to detect the multi-step form.
    dataset_type = request.form.get("dataset_type")
    title = request.form.get("title")
    if dataset_type == "tabular" or title:
        try:
            # Build a DataSetForm without CSRF for this programmatic flow
            form = DataSetForm(meta={"csrf": False})

            # Populate simple fields from the form data
            form.title.data = title
            form.desc.data = request.form.get("desc")
            form.publication_type.data = request.form.get("publication_type")
            form.publication_doi.data = request.form.get("publication_doi")
            form.dataset_doi.data = request.form.get("dataset_doi")
            form.tags.data = request.form.get("tags")

            # Ensure a file_models entry exists and set the csv_filename
            if len(form.file_models.entries) == 0:
                entry = form.file_models.append_entry()
            else:
                entry = form.file_models.entries[0]
            entry_form = getattr(entry, "form", entry)
            entry_form.csv_filename.data = new_filename

            # Validate form (note: CSRF disabled)
            if not form.validate():
                logger.debug("upload (file) form validation failed: %s", form.errors)
                # return errors so the client can show them (keep compatible with JSON/redirect flows)
                return jsonify({"message": form.errors}), 400

            # Create dataset and move files
            logger.info("Creating dataset from /dataset/file/upload...")
            dataset = dataset_service.create_from_form(form=form, current_user=current_user)
            dataset_service.move_file_models(dataset)
        except Exception as exc:
            logger.exception("Error creating dataset from uploaded file: %s", exc)
            return jsonify({"message": str(exc)}), 500

    # Redirect to dataset list in the browser
    return redirect(url_for("dataset.list_dataset"))


@dataset_bp.route("/dataset/file/delete", methods=["POST"])
def delete():
    data = request.get_json()
    filename = data.get("file")
    temp_folder = current_user.temp_folder()
    filepath = os.path.join(temp_folder, filename)

    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"message": "File deleted successfully"})

    return jsonify({"error": "Error: File not found"})


@dataset_bp.route("/dataset/download/<int:dataset_id>", methods=["GET"])
def download_dataset(dataset_id):
    dataset = dataset_service.get_or_404(dataset_id)

    DataSetService().update_download_count(dataset_id)
    
    file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"dataset_{dataset_id}.zip")

    with ZipFile(zip_path, "w") as zipf:
        for subdir, dirs, files in os.walk(file_path):
            for file in files:
                full_path = os.path.join(subdir, file)

                relative_path = os.path.relpath(full_path, file_path)

                zipf.write(
                    full_path,
                    arcname=os.path.join(os.path.basename(zip_path[:-4]), relative_path),
                )

    user_cookie = request.cookies.get("download_cookie")
    if not user_cookie:
        user_cookie = str(uuid.uuid4())  
        resp = make_response(
            send_from_directory(
                temp_dir,
                f"dataset_{dataset_id}.zip",
                as_attachment=True,
                mimetype="application/zip",
            )
        )
        resp.set_cookie("download_cookie", user_cookie)
    else:
        resp = send_from_directory(
            temp_dir,
            f"dataset_{dataset_id}.zip",
            as_attachment=True,
            mimetype="application/zip",
        )

    existing_record = DSDownloadRecord.query.filter_by(
        user_id=current_user.id if current_user.is_authenticated else None,
        dataset_id=dataset_id,
        download_cookie=user_cookie,
    ).first()

    if not existing_record:
        DSDownloadRecordService().create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=user_cookie,
        )

    return resp


@dataset_bp.route("/doi/<path:doi>/", methods=["GET"])
def subdomain_index(doi):

    new_doi = doi_mapping_service.get_new_doi(doi)
    if new_doi:
        return redirect(url_for("dataset.subdomain_index", doi=new_doi), code=302)

    ds_meta_data = dsmetadata_service.filter_by_doi(doi)

    if not ds_meta_data:
        abort(404)

    dataset = ds_meta_data.data_set

    user_cookie = ds_view_record_service.create_cookie(dataset=dataset)
    downloads = DataSetService().get_number_of_downloads(dataset.id)
    resp = make_response(render_template("dataset/view_dataset.html", dataset=dataset, downloads=downloads))
    resp.set_cookie("view_cookie", user_cookie)

    return resp


@dataset_bp.route("/dataset/unsynchronized/<int:dataset_id>/", methods=["GET"])
@login_required
def get_unsynchronized_dataset(dataset_id):

    dataset = dataset_service.get_unsynchronized_dataset(current_user.id, dataset_id)

    if not dataset:
        abort(404)

    downloads = DataSetService().get_number_of_downloads(dataset.id)
    return render_template("dataset/view_dataset.html", dataset=dataset, downloads=downloads)


@dataset_bp.route("/dataset/<int:dataset_id>/sync", methods=["POST"])
@login_required
def sync_dataset(dataset_id):
    """Sync (publish) an unsynchronized dataset via Zenodo/FakeNODO and mark it as synchronized.

    Only the dataset owner may publish.
    """
    logger.debug("sync_dataset called by user=%s for dataset_id=%s", current_user.id if current_user and current_user.is_authenticated else None, dataset_id)

    # Log existence and owner info for debugging why lookup may return None
    try:
        ds_any = dataset_service.repository.get_by_id(dataset_id)
        if ds_any:
            logger.debug("Found dataset id=%s user_id=%s dataset_doi=%s", ds_any.id, getattr(ds_any, 'user_id', None), getattr(getattr(ds_any, 'ds_meta_data', None), 'dataset_doi', None))
        else:
            logger.debug("No dataset found with id=%s", dataset_id)
    except Exception:
        logger.exception("Error fetching dataset by id for debug")

    # Try to fetch dataset regardless of sync status to provide clearer feedback
    ds_any = dataset_service.repository.get_by_id(dataset_id)
    if not ds_any:
        # Truly does not exist: show a user-friendly message and redirect to list
        flash("Dataset no encontrado.", "warning")
        return redirect(url_for("dataset.list_dataset"))

    # Permission check: only owner may publish
    if not (current_user and current_user.is_authenticated and ds_any.user_id == current_user.id):
        # Friendly feedback instead of 403 page
        flash("No tienes permiso para publicar este dataset.", "danger")
        return redirect(url_for("dataset.list_dataset"))

    # Check if it's already synchronized
    existing_doi = getattr(getattr(ds_any, "ds_meta_data", None), "dataset_doi", None)
    if existing_doi:
        # Already published
        flash("Este dataset ya está publicado en el repositorio remoto.", "info")
        return redirect(url_for("dataset.list_dataset"))

    # At this point we have the dataset object to publish
    dataset = ds_any
    print("aqui")

    try:
        # Create deposition
        resp = zenodo_service.create_new_deposition(dataset)
        deposition_id = resp.get("id") if resp else None
        if not deposition_id:
            flash("No se pudo crear la deposition en el repositorio remoto.", "danger")
            return redirect(url_for("dataset.get_unsynchronized_dataset", dataset_id=dataset.id))

        # Save deposition id
        dataset_service.update_dsmetadata(dataset.ds_meta_data_id, deposition_id=deposition_id)

        # Upload files: feature_models and file_models (if present)
        for fm in getattr(dataset, "feature_models", []) + getattr(dataset, "file_models", []):
            try:
                zenodo_service.upload_file(dataset, deposition_id, fm)
            except Exception as exc:
                # Log and continue with other files
                logger.exception("Error subiendo fichero para dataset %s fm=%s: %s", dataset.id, getattr(fm, "id", "?"), exc)

        # Publish deposition
        zenodo_service.publish_deposition(deposition_id)
        doi = zenodo_service.get_doi(deposition_id)

        # Update dataset DOI (this marks it as synchronized)
        dataset_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_doi=doi)        

        flash(f"Dataset publicado correctamente. DOI: {doi}", "success")
        return redirect(url_for("dataset.list_dataset"))
    except Exception as exc:
        logger.exception("Error sincronizando dataset %s: %s", dataset_id, exc)
        flash(f"Error sincronizando dataset: {exc}", "danger")
        return redirect(url_for("dataset.get_unsynchronized_dataset", dataset_id=dataset_id))
