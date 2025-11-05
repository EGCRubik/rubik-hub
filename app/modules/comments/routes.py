from flask import render_template
from app.modules.comments import comments_bp
from app.modules.comments.models import Comments 

@comments_bp.route('/comments', methods=['GET'])
def index():
    comments = Comments.query.all()   
    return render_template('comments/index.html', comments=comments) 