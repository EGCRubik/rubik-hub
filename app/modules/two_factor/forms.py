from flask_wtf import FlaskForm
from wtforms import SubmitField


class TwoFactorForm(FlaskForm):
    submit = SubmitField('Save two_factor')
