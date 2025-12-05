from flask import redirect, render_template, request, url_for, session
from app.modules.two_factor import two_factor_bp
from flask_login import current_user, login_user
from app.modules.auth.services import AuthenticationService

authentication_service = AuthenticationService()


@two_factor_bp.route('/two_factor', methods=['GET', 'POST'])
def index():
    # Si ya está autenticado, redirige a la página principal
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    # Si no viene de un login válido, redirige al login
    pending_user_id = session.get('pending_2fa_user_id')
    if not pending_user_id:
        return redirect(url_for('auth.login'))
    
    # Si es un POST, procesa el código 2FA
    if request.method == 'POST' and request.form:
        user = authentication_service.get_by_id(pending_user_id)
        if not user:
            return redirect(url_for('auth.login'))
        code = request.form.get("two_factor_code")
        print(f"Verifying 2FA code: {code} for user ID: {pending_user_id}")
        login_user(user, remember=True)
        session.pop('pending_2fa_user_id', None)
        return redirect(url_for('public.index'))

    # Muestra la página de 2FA con el user_id pendiente
    return render_template('two_factor/index.html')