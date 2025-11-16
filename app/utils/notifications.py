import logging
import os
import smtplib
from email.message import EmailMessage
from typing import Iterable

from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app import db
from app.modules.auth.models import User as AuthUser
from app.modules.dataset.models import Author as DSAuthor
from app.modules.dataset.models import DSMetaData as DSMetaData

try:
    from app.modules.followAuthor.models import Followauthor
except Exception:
    try:
        from app.modules.followAuthor.models import FollowAuthor as Followauthor
    except Exception:
        raise

try:
    from app.modules.followCommunity.models import Followcommunity
except Exception:
    try:
        from app.modules.followCommunity.models import FollowCommunity as Followcommunity
    except Exception:
        raise
from app.modules.dataset.services import DataSetService

logger = logging.getLogger(__name__)


def _send_email(subject: str, body: str, recipients: Iterable[str]):
    """Send an email using Gmail SMTP. Requires env vars GMAIL_USER and GMAIL_APP_PASSWORD.

    recipients: iterable of email addresses (strings)
    """
    gmail_user = os.getenv("GMAIL_USER")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_user or not gmail_app_password:
        logger.warning("Gmail credentials not configured, skipping email send")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = ", ".join(recipients)
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(gmail_user, gmail_app_password)
            smtp.send_message(msg)
        logger.info("Sent notification email to %s", recipients)
    except Exception as exc:
        logger.exception("Failed to send notification email: %s", exc)


def notify_followers_of_author(user_id, dataset):
    """Notify followers of a single author (by id) about a dataset.

    author_id: integer id of the author whose followers should be notified
    dataset: DataSet instance used to build the email body
    """
    author_id = DataSetService().get_author_id_by_user_id(user_id)
    if not author_id:
        logger.debug("No author_id provided to notify_followers_of_author for dataset %s", getattr(dataset, "id", "?"))
        return

    try:
        follows = Followauthor.query.filter_by(author_id=author_id).all()
    except Exception:
        logger.exception("Error querying Followauthor for author_id=%s dataset=%s", author_id, getattr(dataset, "id", "?"))
        return

    recipients = set()
    for f in follows:
        try:
            follower = getattr(f, "follower", None)
            if follower is None:
                follower = db.session.query(AuthUser).get(f.follower_id)
            if follower and getattr(follower, "email", None):
                recipients.add(follower.email)
        except Exception:
            logger.exception("Error retrieving follower for Followauthor id=%s", getattr(f, "id", "?"))

    logger.info("Notification recipients for author %s dataset %s (count=%s): %s", author_id, getattr(dataset, "id", "?"), len(recipients), list(recipients))
    if not recipients:
        logger.debug("No followers found for author %s (dataset %s)", author_id, getattr(dataset, "id", "?"))
        return

    subject = f"Nuevo dataset publicado: {getattr(dataset.ds_meta_data, 'title', 'sin título')}"
    try:
        link = dataset.get_uvlhub_doi()
    except Exception:
        link = None
    body_lines = [f"Se ha publicado un nuevo dataset: {getattr(dataset.ds_meta_data, 'title', 'sin título')}."]
    if link:
        body_lines.append(f"Ver: {link}")
    body_lines.append("")
    body_lines.append("Puedes desactivar estas notificaciones desde tu cuenta en la plataforma.")

    _send_email(subject, "\n".join(body_lines), recipients)


def notify_followers_of_community(community, dataset):
    """Notify users who follow the given community about a dataset added/approved in it."""
    if not community:
        return

    follows = Followcommunity.query.filter_by(community_id=community.id).all()
    recipients = set()
    for f in follows:
        if getattr(f, "follower", None) and getattr(f.follower, "email", None):
            recipients.add(f.follower.email)

    if not recipients:
        logger.debug("No followers for community %s", getattr(community, "id", "?"))
        return

    subject = f"Nuevo dataset en la comunidad: {getattr(community, 'name', 'sin nombre')}"
    try:
        link = dataset.get_uvlhub_doi()
    except Exception:
        link = None

    body_lines = [f"Se ha añadido un nuevo dataset a la comunidad {getattr(community, 'name', 'sin nombre')}: {getattr(dataset.ds_meta_data, 'title', 'sin título')}."]
    if link:
        body_lines.append(f"Ver: {link}")
    body_lines.append("")
    body_lines.append("Puedes desactivar estas notificaciones desde tu cuenta en la plataforma.")

    _send_email(subject, "\n".join(body_lines), recipients)
