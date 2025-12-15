from flask import jsonify, redirect, render_template, request, url_for, session
from app.modules.two_factor import two_factor_bp
from flask_login import current_user, login_user, login_required
from app.modules.auth.services import AuthenticationService
from app.modules.two_factor.services import TwoFactorService
from io import BytesIO
import base64
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
        totp = pyotp.TOTP(two_factor_service.get_by_user_id(user.id).key)
        print(totp.now())
        if not totp.verify(code):
            return render_template('two_factor/index.html', error="Invalid 2FA code")
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
            session['two_factor_setup_uri'] = uri
            session['two_factor_setup_key'] = key
            # Return JSON with redirect and key for testing/client purposes
            return jsonify({
                "message": "2FA setup initiated",
                "factor_enabled": True,
                "redirect_url": url_for('profile.twofactor_setup'),
                "key": key,
                "uri": uri
            })
            # two_factor_service.create_two_factor_entry(current_user.id, key, uri)
        else:
            two_factor_service.delete_by_user_id(current_user.id)

        user = two_factor_service.update_factor_enabled(factor_enabled)
        db.session.commit()
        return jsonify({"message": "Updated", "factor_enabled": bool(user.factor_enabled)})
    except Exception as exc:
        db.session.rollback()
        return jsonify({"message": f"Error updating 2FA: {exc}"}), 400

@two_factor_bp.route("/two_factor/verify", methods=["POST"])
@login_required
def verify_two_factor():
    code = request.form.get("two_factor_code")
    uri = session.get("two_factor_setup_uri")
    key = session.get("two_factor_setup_key")
    if not code:
        return jsonify({"message": "'two_factor_code' is required"}), 400
    print(f"Verifying 2FA setup code: {code} for user ID: {current_user.id}")

 
    totp = pyotp.TOTP(key)
    if totp.verify(code):
        try:
            two_factor_service.create_two_factor_entry(current_user.id, key, uri)
            two_factor_service.update_factor_enabled(True)
            db.session.commit()
            # Clear setup session data
            session.pop("two_factor_setup_uri", None)
            session.pop("two_factor_setup_key", None)
            return redirect(url_for("profile.my_profile"))
        except Exception as exc:
            db.session.rollback()
            return jsonify({"message": f"Error updating 2FA: {exc}"}), 400
    else:
        return jsonify({"message": "Invalid 2FA code"}), 400

# Serve QR image (PNG) for current user's 2FA setup without storing binary in DB
@two_factor_bp.route('/two_factor/qr_image', methods=['GET'])
@login_required
def qr_image():
    try:
        uri = session.get("two_factor_setup_uri") if session.get("two_factor_setup_uri") else current_user.two_factor.uri
        # Only show QR if 2FA is enabled and we have a stored URI or parameters
        print('Generating QR image, URI from session:', uri)
        if not getattr(current_user, 'factor_enabled', False) and not uri:
            return jsonify({"message": "2FA not enabled"}), 404

        record = two_factor_service.get_by_user_id(current_user.id)
        print(record)
        if (not record or not getattr(record, 'uri', None)) and not uri:
            print(True)
            return jsonify({"message": "QR data not found"}), 404

        # Generate PNG from stored URI on-the-fly
        print('URI:' + (uri if uri else record.uri))
        qr = qrcode.make(uri if uri else record.uri)
        buf = BytesIO()
        qr.save(buf, format='PNG')
        png_bytes = buf.getvalue()
        return (png_bytes, 200, {
            'Content-Type': 'image/png',
            'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0'
        })
    except Exception as exc:
        return jsonify({"message": f"Error generating QR: {exc}"}), 400
