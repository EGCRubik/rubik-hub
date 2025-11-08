from flask_wtf import FlaskForm
from wtforms import SubmitField


class AuthorscommunitiesForm(FlaskForm):
    submit = SubmitField('Save authorsCommunities')
