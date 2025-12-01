import os
import shutil
from datetime import datetime, timezone, timedelta
import uuid
from dotenv import load_dotenv
from random import choice

from app.modules.auth.models import User
from app.modules.dataset.models import Author, DataSet, DSMetaData, DSMetrics, PublicationType, Download, DatasetConcept, DatasetVersion
from app.modules.fileModel.models import FileModel, FMMetaData
from app.modules.hubfile.models import Hubfile
from core.seeders.BaseSeeder import BaseSeeder


class DataSetSeeder(BaseSeeder):

    priority = 2  # Lower priority

    def run(self):

        # Publication types to assign in order
        publication_types = [
            PublicationType.SPECIFICATIONS,
            PublicationType.DISTRIBUTORS,
            PublicationType.SALES,
            PublicationType.MATERIALS,
            PublicationType.OTHER,
            PublicationType.RANKINGS,
            PublicationType.SALES,
            PublicationType.SALES,
            PublicationType.RESULTS,
            PublicationType.REVIEWS
        ]
        # Retrieve users
        user1 = User.query.filter_by(email="user1@example.com").first()
        user2 = User.query.filter_by(email="user2@example.com").first()

        if not user1 or not user2:
            raise Exception("Users not found. Please seed users first.")

        # Create DSMetrics instance
        ds_metrics = DSMetrics(number_of_models="5", number_of_files="50")
        seeded_ds_metrics = self.seed([ds_metrics])[0]

        # Create DSMetaData instances
        ds_meta_data_list = [
            DSMetaData(
                deposition_id=1 + i,
                title=f"Sample dataset {i+1}",
                description=f"Description for dataset {i+1}",
                publication_type=publication_types[i],
                publication_doi=f"10.1234/dataset{i+1}",
                dataset_doi=f"10.1234/dataset{i+1}",
                tags="tag1, tag2",
                ds_metrics_id=seeded_ds_metrics.id,
            )
            for i in range(10)
        ]
        seeded_ds_meta_data = self.seed(ds_meta_data_list)

        # Create Author instances and associate with DSMetaData (one author per ds)
        authors = [
            Author(
                name=f"Author {i+1}",
                affiliation=f"Affiliation {i+1}",
                orcid=f"0000-0000-0000-000{i}",
            )
            for i in range(10)
        ]
        seeded_authors = self.seed(authors)

        # Link each DSMetaData to its single Author
        for i in range(10):
            seeded_ds_meta_data[i].author_id = seeded_authors[i].id
            self.db.session.add(seeded_ds_meta_data[i])
        self.db.session.commit()

        # Create DataSet instances
        datasets = [
            DataSet(
                user_id=user1.id if i % 2 == 0 else user2.id,
                ds_meta_data_id=seeded_ds_meta_data[i].id,
                created_at=datetime.now(timezone.utc),
            )
            for i in range(10)  # 10 datasets
        ]
        seeded_datasets = self.seed(datasets)

        # Create Download entries for each dataset:
        # dataset 10 (last) -> 10 downloads (12 days ago)
        # dataset 9..1 -> N downloads (2 days ago)
        download_records = []
        now = datetime.now(timezone.utc)
        total = len(seeded_datasets)
        for idx, ds in enumerate(seeded_datasets):
            count = idx + 1
            days_ago = 12 if idx == (total - 1) else 2
            download_date = now - timedelta(days=days_ago)
            for _ in range(count):
                download_records.append(Download(dataset_id=ds.id, download_date=download_date))

        if download_records:
            self.seed(download_records)

        # Now create FMMetaData and FileModels for 10 datasets
        fm_meta_data_list = [
            FMMetaData(
                csv_filename=f"file{i+1}.csv",  # Corresponding to 10 CSV files
                title=f"File Model {i+1}",
                description=f"Description for file model {i+1}",
                publication_doi=f"10.1234/fm{i+1}",
                tags="tag1, tag2",
                csv_version="1.0",
            )
            for i in range(10)  # 10 files
        ]
        seeded_fm_meta_data = self.seed(fm_meta_data_list)

        # Link each FMMetaData to the same Author as its DSMetaData (reuse authors)
        for i in range(10):
            # reuse the author created for the dataset metadata
            seeded_fm_meta_data[i].author_id = seeded_authors[i].id
            self.db.session.add(seeded_fm_meta_data[i])
        self.db.session.commit()

        # Create the FileModels and associate them with the Datasets
        file_models = [
            FileModel(data_set_id=seeded_datasets[i].id, fm_meta_data_id=seeded_fm_meta_data[i].id)
            for i in range(10)  # 10 FileModels
        ]
        seeded_file_models = self.seed(file_models)

        # Create files and associate them with FileModels and copy files
        load_dotenv()
        working_dir = os.getenv("WORKING_DIR", "")
        src_folder = os.path.join(working_dir, "app", "modules", "dataset", "csv_examples")
        for i in range(10):  # 10 CSV files
            file_name = f"file{i+1}.csv"
            file_model = seeded_file_models[i]
            dataset = next(ds for ds in seeded_datasets if ds.id == file_model.data_set_id)
            user_id = dataset.user_id

            # Destination folder
            dest_folder = os.path.join(working_dir, "uploads", f"user_{user_id}", f"dataset_{dataset.id}")
            os.makedirs(dest_folder, exist_ok=True)
            shutil.copy(os.path.join(src_folder, file_name), dest_folder)

            file_path = os.path.join(dest_folder, file_name)

            # Create Hubfile for each file
            uvl_file = Hubfile(
                name=file_name,
                checksum=f"checksum{i+1}",
                size=os.path.getsize(file_path),
                file_model_id=file_model.id,
            )
            self.seed([uvl_file])
            
        concepts = []
        versions = []

        for i, dataset in enumerate(seeded_datasets):
            # 1️⃣ Create a DatasetConcept for each dataset
            concept = DatasetConcept(
                conceptual_doi=f"10.9999/concept{i+1}",
                name=f"Concept for dataset {i+1}"
            )
            concepts.append(concept)

        self.seed(concepts)

        # Refresh DB session objects
        self.db.session.flush()

        # 2️⃣ Create versions for each dataset
        for i, dataset in enumerate(seeded_datasets):
            concept = concepts[i]

            # ---- Version 1.0 (major, always present)
            v1 = DatasetVersion(
                concept_id=concept.id,
                dataset_id=dataset.id,
                version_major=1,
                version_minor=0,
                version_doi=f"10.9999/dataset{i+1}.v1",
                changelog="Initial release"
            )
            versions.append(v1)

            # ---- Optional minor version: 1.1
            if i % 2 == 0:  # create for even datasets
                v11 = DatasetVersion(
                    concept_id=concept.id,
                    dataset_id=dataset.id,  # NOTE: For real systems you would duplicate dataset
                    version_major=1,
                    version_minor=1,
                    version_doi=None,
                    changelog="Small fixes and metadata updates"
                )
                versions.append(v11)

            # ---- Optional major version: 2.0
            if i % 3 == 0:  # create for 1/3 datasets
                v2 = DatasetVersion(
                    concept_id=concept.id,
                    dataset_id=dataset.id,
                    version_major=2,
                    version_minor=0,
                    version_doi=f"10.9999/dataset{i+1}.v2",
                    changelog="Major update with structural changes"
                )
                versions.append(v2)

        self.seed(versions)