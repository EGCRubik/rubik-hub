from flask import Blueprint, render_template
from flask_login import login_required

from . import tabular_bp


@tabular_bp.route("/upload", methods=["GET"])
@login_required
def upload_tabular():
    return render_template("tabular/upload_tabular.html")