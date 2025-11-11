from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
import os

from app import db
from app.modules.tabular import tabular_bp
from app.modules.tabular.models import TabularDataset, TabularMetaData
from app.modules.dataset.models import DSMetaData
from app.modules.dataset.forms import DataSetForm


@tabular_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload_tabular():
    if request.method == 'GET':
        # provide an empty DataSetForm so template can render hidden_tag and fields
        form = DataSetForm()
        return render_template("tabular/upload_tabular.html", form=form)

    # POST: create tabular dataset combining basic info and CSV file
    title = request.form.get('title')
    desc = request.form.get('desc')
    publication_type = request.form.get('publication_type')
    publication_doi = request.form.get('publication_doi')
    tags = request.form.get('tags')

    if not title or not desc:
        return render_template("tabular/upload_tabular.html", error="Title and description are required")

    csv_file = request.files.get('csv_file')
    if not csv_file:
        return render_template("tabular/upload_tabular.html", error="CSV file is required")

    try:
        # create ds metadata
        dsmeta = DSMetaData(
            title=title,
            description=desc,
            publication_type=publication_type or 'none',
            publication_doi=publication_doi,
            tags=tags,
        )
        db.session.add(dsmeta)
        db.session.commit()

        # create dataset record of type tabular
        tabds = TabularDataset(user_id=current_user.id, ds_meta_data_id=dsmeta.id)
        db.session.add(tabds)
        db.session.commit()

        # save CSV to user's temp folder
        temp_folder = current_user.temp_folder()
        os.makedirs(temp_folder, exist_ok=True)
        filename = csv_file.filename
        file_path = os.path.join(temp_folder, filename)
        csv_file.save(file_path)

        # create tabular metadata
        delimiter = request.form.get('delimiter') or ','
        encoding = request.form.get('encoding') or 'utf-8'
        has_header = bool(request.form.get('has_header'))
        n_rows = request.form.get('rows_count')

        tabmeta = TabularMetaData(
            dataset_id=tabds.id,
            delimiter=delimiter,
            encoding=encoding,
            has_header=has_header,
            n_rows=int(n_rows) if n_rows else None,
        )
        db.session.add(tabmeta)
        db.session.commit()

    except Exception as e:
        current_app.logger.exception('Error creating tabular dataset: %s', e)
        try:
            db.session.rollback()
        except Exception:
            current_app.logger.exception('Error rolling back session after failure')
        return render_template("tabular/upload_tabular.html", error=str(e))

    return redirect(url_for('dataset.list_dataset'))

@tabular_bp.route("/<int:dataset_id>", methods=["GET"])
@login_required
def show_tabular(dataset_id):
    """Muestra la vista detallada de un dataset tabular."""

    from app.modules.tabular.models import TabularDataset, TabularMetaData

    # 1. Buscar el dataset tabular con su metadata asociada
    tabular_ds = TabularDataset.query \
        .filter_by(id=dataset_id) \
        .first_or_404(description=f"Tabular dataset #{dataset_id} no encontrado")

    meta = tabular_ds.meta_data

    # 2. Validar acceso: solo el propietario o un admin pueden verlo
    if tabular_ds.user_id != current_user.id and not current_user.is_admin:
        return render_template(
            "errors/403.html",
            message="No tienes permiso para acceder a este dataset."
        ), 403

    # 3. (Opcional) Si hay sample_rows en JSON, asegurar que se pueden iterar
    if meta and meta.sample_rows and isinstance(meta.sample_rows, str):
        try:
            import json
            meta.sample_rows = json.loads(meta.sample_rows)
        except Exception:
            current_app.logger.warning(f"Error al parsear sample_rows para dataset {dataset_id}")

    # 4. Renderizar la plantilla
    return render_template(
        "tabular/show.html",
        dataset=tabular_ds,
        meta=meta
    )

@tabular_bp.route("/download/<int:dataset_id>")
@login_required
def download_csv(dataset_id):
    from flask import send_file
    tabular_ds = TabularDataset.query.get_or_404(dataset_id)
    csv_path = tabular_ds.get_csv_path()
    if not csv_path or not os.path.exists(csv_path):
        abort(404, "CSV no encontrado")
    return send_file(csv_path, as_attachment=True)

