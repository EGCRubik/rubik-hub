from flask import render_template
from app.modules.followAuthor import followAuthor_bp


@followAuthor_bp.route('/followAuthor', methods=['GET'])
def index():
    return render_template('followAuthor/index.html')
