"""SQLAlchemy persistence models for the Exalted campaign manager."""

from datetime import datetime, timezone
import secrets
import string

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def utcnow():
    """Return a naive UTC datetime suitable for SQLite DateTime columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def make_invite_code(length=8):
    """Create a human-readable campaign invitation code."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    characters = db.relationship("Character", back_populates="owner", cascade="all, delete-orphan")
    owned_campaigns = db.relationship(
        "Campaign", back_populates="owner", foreign_keys="Campaign.owner_id"
    )
    memberships = db.relationship("CampaignMembership", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username!r}>"


class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False)
    player_name = db.Column(db.String(80), nullable=False, default="")
    caste = db.Column(db.String(20), nullable=False)
    concept = db.Column(db.String(160), nullable=False, default="")
    nature = db.Column(db.String(100), nullable=False, default="")
    anima = db.Column(db.String(160), nullable=False, default="")
    sheet = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    owner = db.relationship("User", back_populates="characters")
    campaign_memberships = db.relationship("CampaignMembership", back_populates="character")

    def __repr__(self):
        return f"<Character {self.name!r} ({self.caste})>"


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    setting_location = db.Column(db.String(100), nullable=False, default="Creation")
    status = db.Column(db.String(20), nullable=False, default="active")
    invite_code = db.Column(db.String(12), unique=True, nullable=False, default=make_invite_code, index=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    owner = db.relationship("User", back_populates="owned_campaigns", foreign_keys=[owner_id])
    memberships = db.relationship("CampaignMembership", back_populates="campaign", cascade="all, delete-orphan")
    sessions = db.relationship("SessionRecord", back_populates="campaign", cascade="all, delete-orphan", order_by="SessionRecord.created_at.desc()")
    npcs = db.relationship("NPC", back_populates="campaign", cascade="all, delete-orphan")
    rolls = db.relationship("RollRecord", back_populates="campaign", cascade="all, delete-orphan")

    @property
    def storyteller(self):
        return self.owner

    def __repr__(self):
        return f"<Campaign {self.name!r}>"


class CampaignMembership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaign.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey("character.id", ondelete="SET NULL"), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="player")
    joined_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    __table_args__ = (db.UniqueConstraint("campaign_id", "user_id", name="uq_campaign_member"),)

    campaign = db.relationship("Campaign", back_populates="memberships")
    user = db.relationship("User", back_populates="memberships")
    character = db.relationship("Character", back_populates="campaign_memberships")

    @property
    def is_storyteller(self):
        return self.role == "storyteller"


class SessionRecord(db.Model):
    __tablename__ = "session_record"

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaign.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    title = db.Column(db.String(120), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="planned")
    summary = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    campaign = db.relationship("Campaign", back_populates="sessions")
    created_by = db.relationship("User")
    notes = db.relationship("SessionNote", back_populates="session", cascade="all, delete-orphan", order_by="SessionNote.created_at.desc()")
    rolls = db.relationship("RollRecord", back_populates="session", cascade="all, delete-orphan")


class SessionNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("session_record.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    content = db.Column(db.Text, nullable=False)
    visibility = db.Column(db.String(12), nullable=False, default="party")
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    session = db.relationship("SessionRecord", back_populates="notes")
    author = db.relationship("User")


class NPC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaign.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default="")
    description = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    campaign = db.relationship("Campaign", back_populates="npcs")


class RollRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaign.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = db.Column(db.Integer, db.ForeignKey("session_record.id", ondelete="SET NULL"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    pool = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    roll_type = db.Column(db.String(20), nullable=False, default="standard")
    dice = db.Column(db.JSON, nullable=False, default=list)
    successes = db.Column(db.Integer, nullable=False, default=0)
    is_botch = db.Column(db.Boolean, nullable=False, default=False)
    succeeded = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    campaign = db.relationship("Campaign", back_populates="rolls")
    session = db.relationship("SessionRecord", back_populates="rolls")
    user = db.relationship("User")
