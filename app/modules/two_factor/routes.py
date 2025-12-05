from flask import jsonify, redirect, render_template, request, url_for, session
from app.modules.two_factor import two_factor_bp
from flask_login import current_user, login_user, login_required
from app.modules.auth.services import AuthenticationService
from app.modules.two_factor.services import TwoFactorService
import time
import pyotp
import qrcode
from app import db

authentication_service = AuthenticationService()
two_factor_service = TwoFactorService()


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

# Update two-factor authentication (2FA) flag for current user
@two_factor_bp.route("/two_factor/update-factor-enabled", methods=["POST"])
@login_required
def update_factor_enabled():
    enabled_value = request.form.get("enabled")
    if enabled_value is None:
        return jsonify({"message": "'enabled' is required"}), 400

    # Accept '1'/'0' or boolean-like strings
    factor_enabled = str(enabled_value).lower() in ("1", "true", "yes")
    try:
        # Use explicit commit/rollback to avoid nested transaction issues
        if factor_enabled:
            key = pyotp.random_base32()
            uri = pyotp.totp.TOTP(key).provisioning_uri(name=current_user.email, issuer_name="RubikHub")
            two_factor_service.create_two_factor_entry(current_user.id, key, uri)
        else:
            two_factor_service.delete_by_user_id(current_user.id)

        user = two_factor_service.update_factor_enabled(factor_enabled)
        db.session.commit()
        return jsonify({"message": "Updated", "factor_enabled": bool(user.factor_enabled)})
    except Exception as exc:
        db.session.rollback()
        return jsonify({"message": f"Error updating 2FA: {exc}"}), 400
