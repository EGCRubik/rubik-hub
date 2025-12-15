from flask_wtf import FlaskForm
from wtforms import BooleanField, FieldList, FormField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import URL, DataRequired, Optional

from app.modules.dataset.models import PublicationType


class AuthorForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    affiliation = StringField("Affiliation")
    orcid = StringField("ORCID")
    gnd = StringField("GND")

    class Meta:
        csrf = False  # disable CSRF because is subform

    def get_author(self):
        return {
            "name": self.name.data,
            "affiliation": self.affiliation.data,
            "orcid": self.orcid.data,
        }


class FileModelForm(FlaskForm):
    csv_filename = StringField("CSV Filename", validators=[DataRequired()])
    title = StringField("Title", validators=[Optional()])
    desc = TextAreaField("Description", validators=[Optional()])
    publication_type = SelectField(
        "Publication type",
        choices=[(pt.value, pt.name.replace("_", " ").title()) for pt in PublicationType],
        validators=[Optional()],
    )
    publication_doi = StringField("Publication DOI", validators=[Optional(), URL()])
    tags = StringField("Tags (separated by commas)")
    version = StringField("CSV Version")
    authors = FieldList(FormField(AuthorForm))

    class Meta:
        csrf = False  # disable CSRF because is subform

    def get_authors(self):
        return [author.get_author() for author in self.authors]

    def get_fmmetadata(self):
        return {
            "csv_filename": self.csv_filename.data,
            "title": self.title.data,
            "description": self.desc.data,
            "publication_type": self.publication_type.data,
            "publication_doi": self.publication_doi.data,
            "tags": self.tags.data,
            "csv_version": self.version.data,
        }

    def get_file_model(self):
        """Return a combined representation of the file model metadata and authors.

        Kept as a convenience for callers that expect a single object per subform.
        """
        return {"fm_meta_data": self.get_fmmetadata(), "authors": self.get_authors()}

    # Backwards-compatible alias used by DataSetForm.get_feature_models()
    def get_feature_model(self):
        return self.get_file_model()


class DataSetForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    desc = TextAreaField("Description", validators=[DataRequired()])
    publication_type = SelectField(
        "Publication type",
        choices=[(pt.value, pt.name.replace("_", " ").title()) for pt in PublicationType],
        validators=[DataRequired()],
    )
    publication_doi = StringField("Publication DOI", validators=[Optional(), URL()])
    dataset_doi = StringField("Dataset DOI", validators=[Optional(), URL()])
    tags = StringField("Tags (separated by commas)")
    authors = FieldList(FormField(AuthorForm))
    file_models = FieldList(FormField(FileModelForm), min_entries=1)

    submit = SubmitField("Submit")

    def get_dsmetadata(self):

        publication_type_converted = self.convert_publication_type(self.publication_type.data)

        return {
            "title": self.title.data,
            "description": self.desc.data,
            "publication_type": publication_type_converted,
            "publication_doi": self.publication_doi.data,
            "dataset_doi": self.dataset_doi.data,
            "tags": self.tags.data,
        }

    def convert_publication_type(self, value):
        for pt in PublicationType:
            if pt.value == value:
                return pt.name
        return "NONE"

    def get_authors(self):
        return [author.get_author() for author in self.authors]

    def get_file_models(self):
        return [fm.get_file_model() for fm in self.file_models]


class VersionUploadForm(FlaskForm):
    """Form for uploading a new version of an existing dataset.
    
    Allows updating the CSV file, optionally updating metadata, and providing
    a changelog/version comment.
    """
    # Optional metadata updates
    title = StringField("Title", validators=[Optional()])
    desc = TextAreaField("Description", validators=[Optional()])
    publication_doi = StringField("Publication DOI", validators=[Optional()])
    tags = StringField("Tags (separated by commas)", validators=[Optional()])
    
    # Version-specific fields
    version_comment = TextAreaField("Version changelog/comment", validators=[DataRequired()])
    is_major = SelectField(
        "Version type",
        choices=[("minor", "Minor update (x.Y)"), ("major", "Major release (X.0)")],
        default="minor",
        validators=[DataRequired()]
    )
    
    modify_file = BooleanField("¿Deseas modificar tu archivo?", validators=[Optional()])
    
    submit = SubmitField("Create New Version")
