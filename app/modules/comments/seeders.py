from core.seeders.BaseSeeder import BaseSeeder
from datetime import datetime, timezone

from app.modules.comments.models import Comments
from app.modules.dataset.models import DataSet


class CommentSeeder(BaseSeeder):

    priority = 3  # para ejecutarse después del DataSetSeeder

    def run(self):
        dataset = DataSet.query.first()

        comments = [
            Comments(
                author_id=1,
                content="Primer comentario",
                date_posted=datetime.now(timezone.utc),
                dataset_id=dataset.id,
            ),
            Comments(
                author_id=2,
                content="Segundo comentario",
                date_posted=datetime.now(timezone.utc),
                dataset_id=dataset.id,
            ),
        ]

        self.seed(comments)
