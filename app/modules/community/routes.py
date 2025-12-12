from flask import abort, jsonify, render_template, request
from flask_login import current_user, login_required  # type: ignore

from app.modules.dataset.models import DataSet

from . import community_bp
from .forms import CommunityForm
from .models import CommunityDatasetStatus
from .services import CommunityDatasetService, CommunityService
from app.modules.auth.models import User

community_service = CommunityService()
link_service = CommunityDatasetService()

def _ensure_curator(community):
    if not community_service.is_curator(community, current_user):
        abort(403)

@community_bp.route("/community/create", methods=["GET", "POST"])
@login_required
def create_community():
    form = CommunityForm()
    if request.method == "POST":
        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400
        community = community_service.create(form, current_user)
        return jsonify({"message": "Community created", "id": community.id}), 201
    return render_template("community/create.html", form=form)

@community_bp.route("/community/list", methods=["GET"])
@login_required
def list_communities():
    return render_template("community/list.html", communities=community_service.get_synchronized(current_user.id))


@community_bp.route("/community/<slug>", methods=["GET"])
def community_detail(slug):
    c = community_service.get_by_slug(slug)
    if not c:
        abort(404)

    is_following = False
    user_datasets = []
    if current_user.is_authenticated:
        # Verifica si el usuario aparece en los seguidores de la comunidad
        is_following = c.followers.filter_by(follower_id=current_user.id).first() is not None
        # Get all user's datasets with version info
        user_datasets = DataSet.query.filter(DataSet.user_id == current_user.id).all()

    return render_template(
        "community/detail.html",
        community=c,
        CommunityDatasetStatus=CommunityDatasetStatus,
        is_following=is_following,
        user_datasets=user_datasets
    )

@community_bp.route("/community/<slug>/delete", methods=["POST"])
@login_required
def delete_community(slug):
    c = community_service.get_by_slug(slug)
    _ensure_curator(c)
    community_service.delete(c)
    return jsonify({"message": "Community deleted"})

# Proponer un dataset para una comunidad
@community_bp.route("/community/<slug>/propose", methods=["POST"])
@login_required
def propose_dataset(slug):
    c = community_service.get_by_slug(slug)
    dataset_id = request.form.get("dataset_id", type=int)
    if not dataset_id:
        return jsonify({"message": "dataset_id is required"}), 400
    ds = DataSet.query.get_or_404(dataset_id)
    # Only the dataset creator/owner can propose it
    if not (
        getattr(ds, "user_id", None) == getattr(current_user, "id", None)
    ):
        return jsonify({"message": "You are not allowed to propose this dataset"}), 403
    link = link_service.propose(c, ds, current_user)
    return jsonify({"message": "Proposed", "link_id": link.id}), 201

# Aceptar/Rechazar (solo curadores)
@community_bp.route("/community/<slug>/proposals/<int:link_id>/approve", methods=["POST"])
@login_required
def approve_dataset(slug, link_id):
    c = community_service.get_by_slug(slug)
    _ensure_curator(c)
    link = link_service.set_status(link_id, CommunityDatasetStatus.APPROVED, current_user)
    return jsonify({"message": "Approved", "link_id": link.id})

@community_bp.route("/community/<slug>/proposals/<int:link_id>/reject", methods=["POST"])
@login_required
def reject_dataset(slug, link_id):
    c = community_service.get_by_slug(slug)
    _ensure_curator(c)
    link = link_service.set_status(link_id, CommunityDatasetStatus.REJECTED, current_user)
    return jsonify({"message": "Rejected", "link_id": link.id})

# Añadir un curador (solo curadores)
@community_bp.route("/community/<slug>/curators/add", methods=["POST"])
@login_required
def add_curator(slug):
    c = community_service.get_by_slug(slug)
    _ensure_curator(c)
    user_id = request.form.get("user_id", type=int)
    if not user_id:
        return jsonify({"message": "user_id is required"}), 400
    user = User.query.get_or_404(user_id)
    community_service.add_curator(c, user)
    return jsonify({"message": "Curator added", "user_id": user.id})