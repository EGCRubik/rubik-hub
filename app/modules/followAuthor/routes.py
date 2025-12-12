from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.modules.dataset.models import Author
from app.modules.followAuthor import followAuthor_bp
from app.modules.followAuthor.models import Followauthor


@followAuthor_bp.route("/authors/<int:author_id>/follow", methods=["POST"])
@login_required
def follow(author_id):
    # Verificar si ya sigue
    existing = Followauthor.query.filter_by(
        author_id=author_id,
        follower_id=current_user.id
    ).first()


    if not existing:
        follow = Followauthor(
            author_id=author_id,
            follower_id=current_user.id
        )
        db.session.add(follow)
        db.session.commit()
        flash("Has seguido al autor.", "success")
    else:
        flash("Ya sigues este autor.", "info")


    return redirect(url_for("public.authors_and_communities"))


@followAuthor_bp.route("/authors/<int:author_id>/unfollow", methods=["POST"])
@login_required
def unfollow(author_id):
    existing = Followauthor.query.filter_by(
        author_id=author_id,
        follower_id=current_user.id
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("Has dejado de seguir al autor.", "warning")

    return redirect(url_for("public.authors_and_communities"))