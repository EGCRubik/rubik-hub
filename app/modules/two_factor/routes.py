from flask import render_template
from app.modules.two_factor import two_factor_bp


@two_factor_bp.route('/two_factor', methods=['GET'])
def index():
    return render_template('two_factor/index.html')
