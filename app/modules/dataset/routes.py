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

from app import db
from app.modules.dataset import dataset_bp
from app.modules.dataset.forms import DataSetForm, VersionUploadForm
from app.modules.dataset.models import DSDownloadRecord
from app.modules.dataset.services import (
    AuthorService,
    DataSetService,
    DOIMappingService,
    DSDownloadRecordService,
    DSMetaDataService,
    DSViewRecordService,
    calculate_checksum_and_size,
)
from app.modules.fakenodo.services import FakenodoService
from app.utils import notifications
from app.utils.notifications import notify_followers_of_author

logger = logging.getLogger(__name__)


dataset_service = DataSetService()
author_service = AuthorService()
dsmetadata_service = DSMetaDataService()


fakenodo_service = FakenodoService()
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
        zenodo_response_json = fakenodo_service.create_new_deposition(dataset)
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
                fakenodo_service.upload_file(dataset, deposition_id, feature_model)

            fakenodo_service.publish_deposition(deposition_id)
            deposition_doi = fakenodo_service.get_doi(deposition_id)
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
        fakenodo_response_json = fakenodo_service.create_new_deposition(dataset)
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
                fakenodo_service.upload_file(dataset, deposition_id, file_model)

            # publish deposition
            fakenodo_service.publish_deposition(deposition_id)

            # update DOI; also set publication_doi if it's empty
            deposition_doi = fakenodo_service.get_doi(deposition_id)
            current_pub_doi = getattr(dataset.ds_meta_data, "publication_doi", None)
            if not current_pub_doi:
                # Set publication_doi to resolvable RubikHub URL
                domain = os.getenv("DOMAIN", "localhost")
                publication_url = f"http://{domain}/doi/{deposition_doi}"
                dataset_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_doi=deposition_doi, publication_doi=publication_url)
            else:
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


@dataset_bp.route("/dataset/view/<int:dataset_id>", methods=["GET"])
def subdomain_index(dataset_id):

    dataset = DataSetService().get_or_404(dataset_id)

    user_cookie = ds_view_record_service.create_cookie(dataset=dataset)
    downloads = DataSetService().get_number_of_downloads(dataset.id)
    resp = make_response(render_template("dataset/view_dataset.html", dataset=dataset, downloads=downloads))
    resp.set_cookie("view_cookie", user_cookie)

    return resp

@dataset_bp.route("/dataset/view/<path:identifier>", methods=["GET"])
def view_dataset_flexible(identifier):
    try:
        dataset_id = int(identifier)
        return redirect(url_for("dataset.subdomain_index", dataset_id=dataset_id))
    except ValueError:
        return redirect(url_for("dataset.resolve_doi", doi=identifier))

@dataset_bp.route("/doi/<path:doi>", methods=["GET"])
def resolve_doi(doi):
    """Resolve a DOI and render the Fakenodo record details alongside the dataset.

    - Look up DSMetaData by dataset_doi to find the dataset for context.
    - Look up Fakenodo record by DOI to display repository data stored in DB.
    """
    try:
        # Dataset context
        dsmd = dsmetadata_service.filter_by_doi(doi)
        dataset = None
        if dsmd and getattr(dsmd, "id", None):
            dataset = dataset_service.repository.model.query.filter_by(ds_meta_data_id=dsmd.id).first()

        # Fakenodo record by DOI
        record = fakenodo_service.get_by_doi(doi)

        return render_template("dataset/fakenodo_record.html", dataset=dataset, record=record)
    except Exception as exc:
        logger.exception("Error resolviendo DOI %s: %s", doi, exc)
        flash("Error resolviendo DOI.", "danger")
        return redirect(url_for("dataset.list_dataset"))

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
    """Sync (publish) an unsynchronized dataset via FakeNODO and mark it as synchronized.

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
        resp = fakenodo_service.create_new_deposition(dataset)
        deposition_id = resp.get("id") if resp else None
        if not deposition_id:
            flash("No se pudo crear la deposition en el repositorio remoto.", "danger")
            return redirect(url_for("dataset.get_unsynchronized_dataset", dataset_id=dataset.id))

        # Save deposition id
        dataset_service.update_dsmetadata(dataset.ds_meta_data_id, deposition_id=deposition_id)

        # Upload files: feature_models and file_models (if present)
        for fm in getattr(dataset, "feature_models", []) + getattr(dataset, "file_models", []):
            try:
                fakenodo_service.upload_file(dataset, deposition_id, fm)
            except Exception as exc:
                # Log and continue with other files
                logger.exception("Error subiendo fichero para dataset %s fm=%s: %s", dataset.id, getattr(fm, "id", "?"), exc)

        # Publish deposition
        fakenodo_service.publish_deposition(deposition_id)
        doi = fakenodo_service.get_doi(deposition_id)

        # Update dataset DOI (this marks it as synchronized); also set publication_doi if empty
        current_pub_doi = getattr(dataset.ds_meta_data, "publication_doi", None)
        if not current_pub_doi:
            domain = os.getenv("DOMAIN", "localhost")
            publication_url = f"http://{domain}/doi/{doi}"
            dataset_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_doi=doi, publication_doi=publication_url)
        else:
            dataset_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_doi=doi)

        flash(f"Dataset publicado correctamente. DOI: {doi}", "success")
        return redirect(url_for("dataset.list_dataset"))
    except Exception as exc:
        logger.exception("Error sincronizando dataset %s: %s", dataset_id, exc)
        flash(f"Error sincronizando dataset: {exc}", "danger")
        return redirect(url_for("dataset.get_unsynchronized_dataset", dataset_id=dataset_id))


@dataset_bp.route("/dataset/view/<int:dataset_id>/newversion", methods=["GET", "POST"])
@login_required
def upload_new_version(dataset_id):
    """Create a new version of an existing dataset."""
    dataset = dataset_service.get_or_404(dataset_id)
    
    # Permission check: only owner
    if dataset.user_id != current_user.id:
        flash("No tienes permiso para crear una nueva versión.", "danger")
        return redirect(url_for("dataset.list_dataset"))
    
    form = VersionUploadForm()
    
    if request.method == "GET":
        # Pre-fill form with current dataset data
        form.title.data = dataset.ds_meta_data.title
        form.desc.data = dataset.ds_meta_data.description
        form.publication_doi.data = dataset.ds_meta_data.publication_doi
        form.tags.data = dataset.ds_meta_data.tags
        return render_template("dataset/upload_version.html", form=form, dataset=dataset)
    
    # POST: create new version
    if not form.validate_on_submit():
        return render_template("dataset/upload_version.html", form=form, dataset=dataset)
    
    # Get CSV file (optional)
    csv_file = None
    filename = None
    dest_path = None
    
    if form.modify_file.data:
        csv_file = request.files.get("csv_file")
        if not csv_file or csv_file.filename == "":
            flash("Debes subir un archivo CSV si seleccionas modificar el archivo.", "danger")
            return render_template("dataset/upload_version.html", form=form, dataset=dataset)
        
        filename = secure_filename(csv_file.filename)
        if not filename.lower().endswith(".csv"):
            flash("El archivo debe ser .csv", "danger")
            return render_template("dataset/upload_version.html", form=form, dataset=dataset)
        
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
        
        csv_file.save(dest_path)
    
    dataset_service.update_dsmetadata(
        dataset.ds_meta_data_id,
        title=form.title.data,
        description=form.desc.data,
        publication_doi=form.publication_doi.data,
        tags=form.tags.data
    )
    
    current_version = dataset.version
    concept_versions = current_version.concept.versions if current_version and current_version.concept else []
    
    if concept_versions:
        latest_version = max(concept_versions, key=lambda v: (v.version_major, v.version_minor))
        highest_major = latest_version.version_major
        highest_minor = latest_version.version_minor
    else:
        highest_major = current_version.version_major
        highest_minor = current_version.version_minor
    
    is_major = form.is_major.data == "major"
    
    if is_major:
        new_major = highest_major + 1
        new_minor = 0
    else:
        new_major = highest_major
        new_minor = highest_minor + 1
    
    version = dataset_service.create_version(
        dataset=dataset,
        major=new_major,
        minor=new_minor,
        changelog=form.version_comment.data
    )
    new_dataset = version.data_set
    
    if form.modify_file.data and dest_path and filename:
        working_dir = os.getenv("WORKING_DIR", "")
        new_dataset_dir = os.path.join(working_dir, "uploads", f"user_{current_user.id}", f"dataset_{new_dataset.id}")
        
        for file in os.listdir(new_dataset_dir):
            if file.lower().endswith(".csv"):
                os.remove(os.path.join(new_dataset_dir, file))
        
        shutil.move(dest_path, new_dataset_dir)
        
        if new_dataset.file_models:
            fm = new_dataset.file_models[0]
            if fm.fm_meta_data:
                fm.fm_meta_data.csv_filename = filename
                db.session.add(fm.fm_meta_data)
            if fm.files:
                hubfile = fm.files[0]
                hubfile.name = filename
                new_path = os.path.join(new_dataset_dir, filename)
                checksum, size = calculate_checksum_and_size(new_path)
                hubfile.checksum = checksum
                hubfile.size = size
                db.session.add(hubfile)
        
        db.session.commit()

        try:
            dep_id = getattr(dataset.ds_meta_data, "deposition_id", None)
            if dep_id:
                fakenodo_service.set_dataset_version(
                    deposition_id=dep_id, 
                    version_major=new_major, 
                    version_minor=new_minor,
                    append_to_versions=False  
                )
                if new_dataset.file_models:
                    fakenodo_service.upload_file(new_dataset, dep_id, new_dataset.file_models[0])
                fakenodo_service.publish_deposition(dep_id)
                new_doi = fakenodo_service.get_doi(dep_id)
                current_pub_doi_new = getattr(new_dataset.ds_meta_data, "publication_doi", None)
                if not current_pub_doi_new:
                    domain = os.getenv("DOMAIN", "localhost")
                    publication_url = f"http://{domain}/doi/{new_doi}"
                    dataset_service.update_dsmetadata(new_dataset.ds_meta_data_id, dataset_doi=new_doi, publication_doi=publication_url)
                else:
                    dataset_service.update_dsmetadata(new_dataset.ds_meta_data_id, dataset_doi=new_doi)
        except Exception as exc:
            logger.exception("Error publishing new version to FakeNODO: %s", exc)
            flash("Se creó la nueva versión, pero falló la publicación en el repositorio.", "warning")
    else:
        db.session.commit()

        try:
            dep_id = getattr(dataset.ds_meta_data, "deposition_id", None)
            if dep_id:
                fakenodo_service.set_dataset_version(deposition_id=dep_id, version_major=new_major, version_minor=new_minor)
        except Exception as exc:
            logger.exception("Error updating deposition dataset_version without publishing: %s", exc)

    flash(
        f"Nueva versión {new_major}.{new_minor} creada correctamente!"
        + (" Se ha publicado y generado un nuevo DOI." if form.modify_file.data else " (edición de metadatos, DOI sin cambios)."),
        "success",
    )
    return redirect(url_for("dataset.list_dataset"))


@dataset_bp.route("/dataset/top", methods=["GET"])
def get_top_datasets():
    """Muestra los 3 datasets más descargados"""
    try:
        top = dataset_service.get_top_downloaded_last_week(limit=3)
        return render_template("dataset/top_datasets.html", top_datasets=top)
    except Exception:
        logger.exception("Error loading top datasets")
        return render_template("dataset/top_datasets.html", top_datasets=[])