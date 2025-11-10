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