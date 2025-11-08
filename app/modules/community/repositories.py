from app.modules.community.models import Community, CommunityCurator, CommunityDataset
from core.repositories.BaseRepository import BaseRepository


class CommunityRepository(BaseRepository):
    def __init__(self):
        super().__init__(Community)

    def get_synchronized(self, current_user_id: int) -> Community:
        return (
            self.model.query.join(CommunityCurator)
            .filter(CommunityCurator.user_id == current_user_id)
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_unsynchronized(self, current_user_id: int) -> Community:
        return (
            self.model.query.join(CommunityCurator)
            .filter(CommunityCurator.user_id == current_user_id)
            .order_by(self.model.created_at.desc())
            .all()
        )
