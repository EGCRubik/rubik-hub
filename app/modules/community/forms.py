from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp


class CommunityForm(FlaskForm):
    name = StringField('Community Name', validators=[DataRequired(), Length(max=100)])
    slug = StringField("Slug", validators=[
        DataRequired(),
        Length(max=80),
        Regexp(r"^[a-z0-9-]+$", message="Use only lowercase, numbers and hyphens")
    ])
    description = TextAreaField('Description', validators=[Optional()])
    banner_color = StringField('Banner Color', validators=[Optional(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Invalid hex color code.')])
    submit = SubmitField('Save community')
