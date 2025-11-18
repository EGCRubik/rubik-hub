import logging
from datetime import datetime, timezone
from typing import Optional

from flask_login import current_user
from sqlalchemy import desc, func

from app.modules.dataset.models import Author, DataSet, DOIMapping, DSDownloadRecord, DSMetaData, DSViewRecord, BaseDataset, Download
from core.repositories.BaseRepository import BaseRepository

from app import db

logger = logging.getLogger(__name__)


class DownloadRepository(BaseRepository):
    def __init__(self):
        super().__init__(Download)

    def create_download_record(self, dataset_id: int) -> Download:
        return self.create(
            dataset_id=dataset_id,
            download_date=datetime.now(timezone.utc),
        )

class AuthorRepository(BaseRepository):
    def __init__(self):
        super().__init__(Author)


class DSDownloadRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSDownloadRecord)

    def total_dataset_downloads(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0


class DSMetaDataRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSMetaData)

    def filter_by_doi(self, doi: str) -> Optional[DSMetaData]:
        return self.model.query.filter_by(dataset_doi=doi).first()


class DSViewRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSViewRecord)

    def total_dataset_views(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0

    def the_record_exists(self, dataset: DataSet, user_cookie: str):
        return self.model.query.filter_by(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset.id,
            view_cookie=user_cookie,
        ).first()

    def create_new_record(self, dataset: DataSet, user_cookie: str) -> DSViewRecord:
        return self.create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset.id,
            view_date=datetime.now(timezone.utc),
            view_cookie=user_cookie,
        )


class DataSetRepository(BaseRepository):
    def __init__(self):
        # Use BaseDataset as the repository model so that all dataset polymorphic
        # types (uvl, tabular, etc.) are returned by queries. Previously the
        # module exported `DataSet = UVLDataset` which caused tabular datasets
        # to be excluded from listings.
        super().__init__(BaseDataset)

    def get_synchronized(self, current_user_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DSMetaData.dataset_doi.isnot(None))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_unsynchronized(self, current_user_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DSMetaData.dataset_doi.is_(None))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_unsynchronized_dataset(self, current_user_id: int, dataset_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DataSet.id == dataset_id, DSMetaData.dataset_doi.is_(None))
            .first()
        )

    def count_synchronized_datasets(self):
        return self.model.query.join(DSMetaData).filter(DSMetaData.dataset_doi.isnot(None)).count()

    def count_unsynchronized_datasets(self):
        return self.model.query.join(DSMetaData).filter(DSMetaData.dataset_doi.is_(None)).count()

    def latest_synchronized(self):
        return (
            self.model.query.join(DSMetaData)
            .filter(DSMetaData.dataset_doi.isnot(None))
            .order_by(desc(self.model.id))
            .limit(5)
            .all()
        )
    
    def get_number_of_downloads(self, dataset_id: int) -> int:
        dataset = self.model.query.filter_by(id=dataset_id).first()
        if not dataset:
            return 0

        return dataset.downloads.count()

    def get_by_id(self, dataset_id: int) -> Optional[DataSet]:
        return DataSet.query.get(dataset_id)

    def update_download_count(self, dataset, new_count):
        if not dataset:
            return None

        fm_metrics = dataset.file_models[0].fm_meta_data.fm_metrics  # Assuming one FileModel per DataSet
        if fm_metrics:
            fm_metrics.number_of_downloads = new_count
            db.session.add(fm_metrics)
            db.session.commit()
            return fm_metrics

        return None


class DOIMappingRepository(BaseRepository):
    def __init__(self):
        super().__init__(DOIMapping)

    def get_new_doi(self, old_doi: str) -> str:
        return self.model.query.filter_by(dataset_doi_old=old_doi).first()
