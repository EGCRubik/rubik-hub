from flask_wtf import FlaskForm
from wtforms import SubmitField


class FollowauthorForm(FlaskForm):
    submit = SubmitField('Save followAuthor')
