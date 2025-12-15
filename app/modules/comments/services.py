# app/modules/comments/services.py
from flask import flash

from app import db
from app.modules.comments.models import Comments
from app.modules.dataset.models import DataSet


class CommentsService:
    def create_comment(self, dataset_id, author_id, content):
        dataset = DataSet.query.get_or_404(dataset_id)

        if not content:
            flash("Comment cannot be empty.", "danger")
            return None, dataset

        comment = Comments(
            author_id=author_id,
            dataset_id=dataset.id,
            content=content
        )

        db.session.add(comment)
        db.session.commit()
        flash("Comment added successfully!", "success")
        return comment, dataset

    def delete_comment(self, comment_id, current_user):
        comment = Comments.query.get_or_404(comment_id)
        dataset = comment.dataset

        if current_user.profile.id != comment.author_id and current_user.id != dataset.user_id:
            flash("You don't have permission to delete this comment.", "danger")
            return None, dataset

        db.session.delete(comment)
        db.session.commit()
        flash("Comment deleted successfully!", "success")
        return comment, dataset
    
# He utilizado parcialmente la inteligencia artificial (IA) como herramienta de apoyo durante el desarrollo y modificación de este archivo de código. 
# La IA me ha ayudado a entender, optimizar y automatizar ciertas tareas, pero la implementación final y las decisiones clave han sido realizadas por mí.
