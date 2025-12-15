import logging

from flask import redirect, render_template, url_for
from flask_login import current_user

from app.modules.community.services import CommunityService
from app.modules.dataset.services import AuthorService, DataSetService
from app.modules.fileModel.services import FileModelService
from app.modules.public import public_bp

logger = logging.getLogger(__name__)


@public_bp.route("/")
def index():
    logger.info("Access index")
    dataset_service = DataSetService()
    file_model_service = FileModelService()

    # Statistics: total datasets and file models
    datasets_counter = dataset_service.count_synchronized_datasets()
    file_models_counter = file_model_service.count_file_models()

    # Statistics: total downloads
    total_dataset_downloads = dataset_service.total_dataset_downloads()
    total_file_model_downloads = file_model_service.total_file_model_downloads()

    # Statistics: total views
    total_dataset_views = dataset_service.total_dataset_views()
    total_file_model_views = file_model_service.total_file_model_views()

    return render_template(
        "public/index.html",
        datasets=dataset_service.latest_synchronized(),
        datasets_counter=datasets_counter,
        total_dataset_downloads=total_dataset_downloads,
        total_dataset_views=total_dataset_views,
    )


@public_bp.route("/authors-and-communities")
def authors_and_communities():
    """Render a page listing authors and communities."""
    logger.info("Access authors and communities view")
    
    # Load authors
    author_service = AuthorService()
    author_model = author_service.repository.model
    authors_q = author_model.query.all()
    authors = [a.to_dict() for a in authors_q]
    for idx, a in enumerate(authors):
        if current_user.is_authenticated:
            a['is_following'] = authors_q[idx].followers.filter_by(follower_id=current_user.id).first() is not None
        a['id'] = authors_q[idx].id

    # Load communities
    community_service = CommunityService()
    communities = community_service.list_all()

    return render_template('public/authors_communities.html', authors=authors, communities=communities)
