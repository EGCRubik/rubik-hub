from flask import render_template

from app.modules.fileModel import filemodel_bp


@filemodel_bp.route("/filemodel", methods=["GET"])
def index():
    return render_template("filemodel/index.html")
