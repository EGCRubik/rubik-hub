import logging

from flask import render_template

from app.modules.authorsCommunities import authorsCommunities_bp
from app.modules.authorsCommunities.services import AuthorscommunitiesService
from app.modules.community.services import CommunityService

# Services used to collect authors and communities data
from app.modules.dataset.services import AuthorService

logger = logging.getLogger(__name__)


@authorsCommunities_bp.route('/authors-and-communities', methods=['GET'])
def index():
    """Render a page listing authors and communities.

    Authors are taken from the dataset.Author model (via AuthorService).
    Communities are taken from the Authorscommunities model. Since the
    community model may have custom fields, we build a dictionary from the
    model instance's __dict__ filtering out SQLAlchemy internals.
    """
    # Load authors
    author_service = AuthorService()
    author_model = author_service.repository.model
    authors_q = author_model.query.all()
    authors = [a.to_dict() for a in authors_q]

    # Load communities.
    community_service = CommunityService()
    communities = community_service.list_all()

    return render_template('authorsCommunities/index.html', authors=authors, communities=communities)

    comm_model = community_service.repository.model
    try:
        comm_q = comm_model.query.all()
    except Exception as exc:  # pragma: no cover - defensive for dev envs
        logger.warning("Could not query communities table: %s", exc)
        comm_q = []

    def model_to_dict(obj):
        data = {}
        for k, v in getattr(obj, "__dict__", {}).items():
            if k.startswith("_"):
                continue
            data[k] = v
        return data

    communities = [model_to_dict(c) for c in comm_q]

    return render_template('authorsCommunities/index.html', authors=authors, communities=communities)
