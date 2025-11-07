from flask import Blueprint

from . import tabular_bp


@tabular_bp.route("/upload")
def upload_tabular():
    return "Aquí irá la subida de CSVs de Rubik"