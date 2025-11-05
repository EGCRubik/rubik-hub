from flask import render_template, request, redirect, url_for, flash
from app.modules.comments import comments_bp
from app.modules.comments.models import Comments 
from flask_login import current_user, login_required
from app import db
from app.modules.dataset.models import DataSet
from app.modules.comments.models import Comments

@comments_bp.route('/comments', methods=['GET'])
def index():
    comments = Comments.query.all()   
    return render_template('comments/index.html', comments=comments) 

@comments_bp.route('/create/<int:dataset_id>', methods=['POST'])
@login_required
def create_comment(dataset_id):
    dataset = DataSet.query.get_or_404(dataset_id)
    content = request.form.get('content')

    if not content:
        flash("Comment cannot be empty.", "danger")
        return redirect(url_for("dataset.view_dataset", dataset_id=dataset.id))

    comment = Comments(
        author_id=current_user.profile.id,  # O como tengas vinculado al Author
        dataset_id=dataset.id,
        content=content
    )

    db.session.add(comment)
    db.session.commit()
    flash("Comment added successfully!", "success")
    return render_template("dataset/view_dataset.html", dataset=dataset)

