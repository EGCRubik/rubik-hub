from flask import redirect, render_template, request, url_for, jsonify, session
from flask_login import current_user, login_user, logout_user, login_required

from app.modules.auth import auth_bp
from app.modules.auth.forms import LoginForm, SignupForm
from app.modules.auth.services import AuthenticationService
from app.modules.profile.services import UserProfileService

authentication_service = AuthenticationService()
user_profile_service = UserProfileService()


@auth_bp.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        if not authentication_service.is_email_available(email):
            return render_template("auth/signup_form.html", form=form, error=f"Email {email} in use")

        try:
            user = authentication_service.create_with_profile(**form.data)
        except Exception as exc:
            return render_template("auth/signup_form.html", form=form, error=f"Error creating user: {exc}")

        # Log user
        login_user(user, remember=True)
        return redirect(url_for("public.index"))

    return render_template("auth/signup_form.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    session.pop("pending_2fa_user_id", None)
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        if authentication_service.login(form.email.data, form.password.data):
            user = authentication_service.get_user_by_email(form.email.data)
            if user and getattr(user, "factor_enabled", True):
                # No iniciar sesión aún: guardar usuario pendiente en sesión y redirigir a 2FA
                session["pending_2fa_user_id"] = user.id
                return redirect(url_for("two_factor.index"))
            # Si no tiene 2FA, iniciar sesión normalmente
            if user:
                login_user(user, remember=True)
                return redirect(url_for("public.index"))

        return render_template("auth/login_form.html", form=form, error="Invalid credentials")

    return render_template("auth/login_form.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("public.index"))


# Update two-factor authentication (2FA) flag for current user
@auth_bp.route("/auth/update-factor-enabled", methods=["POST"])
@login_required
def update_factor_enabled():
    enabled_value = request.form.get("enabled")
    if enabled_value is None:
        return jsonify({"message": "'enabled' is required"}), 400

    # Accept '1'/'0' or boolean-like strings
    factor_enabled = str(enabled_value).lower() in ("1", "true", "yes")
    try:
        user = authentication_service.update_factor_enabled(current_user.id, factor_enabled)
        return jsonify({"message": "Updated", "factor_enabled": bool(user.factor_enabled)})
    except Exception as exc:
        return jsonify({"message": f"Error updating 2FA: {exc}"}), 400
