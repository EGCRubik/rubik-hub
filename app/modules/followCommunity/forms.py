from flask_wtf import FlaskForm
from wtforms import SubmitField


class FollowcommunityForm(FlaskForm):
    submit = SubmitField('Save followCommunity')
