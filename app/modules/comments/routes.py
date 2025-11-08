from flask import render_template, request, redirect, url_for, flash
from app.modules.comments import comments_bp
from app.modules.comments.models import Comments 
from flask_login import current_user, login_required
from app import db
from app.modules.dataset.models import DataSet
from app.modules.comments.models import Comments
from app.modules.comments.services import CommentsService
comments_service = CommentsService()

@comments_bp.route('/create/<int:dataset_id>', methods=['POST'])
@login_required
def create_comment(dataset_id):
    content = request.form.get('content')
    author_id = current_user.profile.id

    comment, dataset = comments_service.create_comment(dataset_id, author_id, content)

    if comment is None:
        return redirect(url_for("dataset.view_dataset", dataset_id=dataset.id))

    return render_template("dataset/view_dataset.html", dataset=dataset)


@comments_bp.route('/delete/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    result, dataset = comments_service.delete_comment(comment_id, current_user)

    if result is None:
        return redirect(url_for("dataset.dataset", id=dataset.id))

    return render_template("dataset/view_dataset.html", dataset=dataset)
