"""Flask-WTF forms. Dynamic character dots are validated server-side in routes.py."""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateTimeLocalField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Length, NumberRange, Optional

CASTES = [
    ("Dawn", "Dawn — Warrior"),
    ("Zenith", "Zenith — Priest / Leader"),
    ("Twilight", "Twilight — Scholar / Sorcerer"),
    ("Night", "Night — Spy / Assassin"),
    ("Eclipse", "Eclipse — Ambassador"),
]


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=40)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        "Confirm password", validators=[DataRequired(), EqualTo("password", message="Passwords must match.")]
    )
    submit = SubmitField("Create account")


class LoginForm(FlaskForm):
    identity = StringField("Username or email", validators=[DataRequired(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Enter Creation")


class CharacterForm(FlaskForm):
    name = StringField("Character name", validators=[DataRequired(), Length(max=80)])
    player_name = StringField("Player", validators=[DataRequired(), Length(max=80)])
    caste = SelectField("Caste", choices=CASTES, validators=[DataRequired()])
    concept = StringField("Concept", validators=[Optional(), Length(max=160)])
    nature = StringField("Nature", validators=[Optional(), Length(max=100)])
    anima = StringField("Anima", validators=[Optional(), Length(max=160)])
    personal_motes = StringField("Personal motes", validators=[Optional(), Length(max=40)])
    peripheral_motes = StringField("Peripheral motes", validators=[Optional(), Length(max=40)])
    backgrounds = TextAreaField("Backgrounds", validators=[Optional(), Length(max=4000)])
    submit = SubmitField("Save character")


class CampaignForm(FlaskForm):
    name = StringField("Campaign name", validators=[DataRequired(), Length(max=100)])
    setting_location = StringField("Starting location", default="Creation", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Campaign premise", validators=[Optional(), Length(max=5000)])
    submit = SubmitField("Save campaign")


class JoinCampaignForm(FlaskForm):
    invite_code = StringField("Invitation code", validators=[DataRequired(), Length(min=4, max=12)])
    character_id = SelectField("Character", coerce=int, choices=[(0, "Join without a character yet")])
    submit = SubmitField("Join campaign")


class CharacterSelectForm(FlaskForm):
    character_id = SelectField("Campaign character", coerce=int, choices=[(0, "No character assigned")])
    submit = SubmitField("Update character")


class SessionForm(FlaskForm):
    title = StringField("Session title", validators=[DataRequired(), Length(max=120)])
    scheduled_at = DateTimeLocalField("Date and time", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    summary = TextAreaField("Preparation / recap", validators=[Optional(), Length(max=8000)])
    submit = SubmitField("Create session")


class SessionNoteForm(FlaskForm):
    content = TextAreaField("Session note", validators=[DataRequired(), Length(max=10000)])
    visibility = SelectField(
        "Visibility", choices=[("party", "Visible to the whole party"), ("gm", "Storyteller only")]
    )
    submit = SubmitField("Add note")


class NPCForm(FlaskForm):
    name = StringField("NPC name", validators=[DataRequired(), Length(max=100)])
    role = StringField("Role / faction", validators=[Optional(), Length(max=100)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=4000)])
    submit = SubmitField("Add NPC")


class DiceRollForm(FlaskForm):
    pool = IntegerField("Dice pool", default=5, validators=[InputRequired(), NumberRange(min=0, max=50)])
    difficulty = IntegerField("Difficulty", default=1, validators=[DataRequired(), NumberRange(min=1, max=10)])
    roll_type = SelectField(
        "Roll type", choices=[("standard", "Standard action"), ("damage", "Damage")], default="standard"
    )
    submit = SubmitField("Roll d10s")
