from flask_wtf import FlaskForm
from wtforms import SubmitField


class FileModelForm(FlaskForm):
    submit = SubmitField("Save filemodel")
