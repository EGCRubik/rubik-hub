from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.modules.followCommunity import followCommunity_bp
from app.modules.followCommunity.models import Followcommunity

@followCommunity_bp.route("/communities/follows")
def index():
    follows = Followcommunity.query.all()
    return render_template("followCommunity/index.html", follows=follows)

@followCommunity_bp.route("/communities/<int:community_id>/follow", methods=["POST"])
@login_required
def follow(community_id):
    # Verificar si ya sigue
    existing = Followcommunity.query.filter_by(
        community_id=community_id,
        follower_id=current_user.id
    ).first()

    if not existing:
        follow = Followcommunity(
            community_id=community_id,
            follower_id=current_user.id
        )
        db.session.add(follow)
        db.session.commit()
        flash("Has seguido la comunidad.", "success")
    else:
        flash("Ya sigues esta comunidad.", "info")

    return redirect(url_for("community.view", community_id=community_id))


@followCommunity_bp.route("/communities/<int:community_id>/unfollow", methods=["POST"])
@login_required
def unfollow(community_id):
    existing = Followcommunity.query.filter_by(
        community_id=community_id,
        follower_id=current_user.id
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("Has dejado de seguir la comunidad.", "warning")

    return redirect(url_for("community.view", community_id=community_id))