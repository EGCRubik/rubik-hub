from flask_wtf import FlaskForm
from wtforms import SubmitField


class CommentsForm(FlaskForm):
    submit = SubmitField('Save comments')
