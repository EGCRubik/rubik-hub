from sqlalchemy import Enum as SQLAlchemyEnum

from app import db
from app.modules.dataset.models import Author, PublicationType


class FileModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_set_id = db.Column(db.Integer, db.ForeignKey("data_set.id"), nullable=False)
    fm_meta_data_id = db.Column(db.Integer, db.ForeignKey("fm_meta_data.id"))
    files = db.relationship("Hubfile", backref="file_model", lazy=True, cascade="all, delete")
    fm_meta_data = db.relationship("FMMetaData", uselist=False, backref="file_model", cascade="all, delete")

    def get_number_of_downloads(self) -> int:
    # Verifica si existe fm_meta_data
        if not self.fm_meta_data:
            # Si no existe, crea un nuevo fm_meta_data y fm_metrics
            new_metrics = FMMetrics(number_of_downloads=0)  # Inicializa con un valor por defecto, por ejemplo 0
            db.session.add(new_metrics)
            db.session.flush()  # Asegura que el objeto se guarde y obtenga un ID

            new_fm_meta_data = FMMetaData(
                csv_filename="default.csv",  # Aquí pon valores predeterminados o vacíos según lo necesario
                title="Default Title",
                description="Default Description",
                fm_metrics=new_metrics  # Asocia el nuevo FMMetrics
            )
            db.session.add(new_fm_meta_data)
            db.session.flush()  # Asegura que fm_meta_data esté persistido

            # Asocia el nuevo fm_meta_data al FileModel
            self.fm_meta_data = new_fm_meta_data
            db.session.add(self)

        # Verifica si existe fm_metrics, si no, crea uno nuevo
        if not self.fm_meta_data.fm_metrics:
            new_metrics = FMMetrics(number_of_downloads=0)
            db.session.add(new_metrics)
            db.session.flush()  # Asegura que el objeto se guarde y obtenga un ID

            self.fm_meta_data.fm_metrics = new_metrics
            db.session.add(self.fm_meta_data)

        # Ahora que tenemos fm_meta_data y fm_metrics válidos, retorna el número de descargas
        return self.fm_meta_data.fm_metrics.number_of_downloads


    def __repr__(self):
        return f"FileModel<{self.id}>"


class FMMetaData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    csv_filename = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    publication_doi = db.Column(db.String(120))
    tags = db.Column(db.String(120))
    csv_version = db.Column(db.String(120))
    fm_metrics_id = db.Column(db.Integer, db.ForeignKey("fm_metrics.id"))
    fm_metrics = db.relationship("FMMetrics", uselist=False, backref="fm_meta_data")

    # Single author for the file-level metadata (business rule: one author per FMMetaData)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=True)
    author = db.relationship("Author", backref=db.backref("fm_meta_datas", lazy=True), uselist=False)

    def __repr__(self):
        return f"FMMetaData<{self.title}"


class FMMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    solver = db.Column(db.Text)
    not_solver = db.Column(db.Text)

    def __repr__(self):
        return f"FMMetrics<solver={self.solver}, not_solver={self.not_solver}>"


#He utilizado parcialmente la inteligencia artificial (IA) como herramienta de apoyo durante el desarrollo y modificación de este archivo de código.
#La IA me ha ayudado a entender, optimizar y automatizar ciertas tareas, pero la implementación final y las decisiones clave han sido realizadas por mí.