"""HTTP routes and application workflows for Exalted Chronicle."""

import secrets

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_

from .extensions import db
from .forms import (
    CampaignForm,
    CharacterForm,
    CharacterSelectForm,
    DiceRollForm,
    JoinCampaignForm,
    LoginForm,
    NPCForm,
    RegistrationForm,
    SessionForm,
    SessionNoteForm,
)
from .models import (
    Campaign,
    CampaignMembership,
    Character,
    NPC,
    RollRecord,
    SessionNote,
    SessionRecord,
    User,
)

main = Blueprint("main", __name__)

ATTRIBUTE_GROUPS = {
    "physical": ["strength", "dexterity", "stamina"],
    "social": ["charisma", "manipulation", "appearance"],
    "mental": ["perception", "intelligence", "wits"],
}
ABILITY_GROUPS = {
    "Dawn": ["archery", "brawl", "martial-arts", "thrown", "melee"],
    "Zenith": ["endurance", "performance", "presence", "resistance", "survival"],
    "Twilight": ["craft", "investigation", "lore", "medicine", "occult"],
    "Night": ["athletics", "awareness", "dodge", "larceny", "stealth"],
    "Eclipse": ["bureaucracy", "linguistics", "ride", "sail", "socialize"],
}
ALL_ABILITIES = [ability for group in ABILITY_GROUPS.values() for ability in group]
VIRTUES = ["compassion", "conviction", "temperance", "valor"]


def _int_value(formdata, key, default, minimum, maximum, errors):
    raw = formdata.get(key, str(default))
    try:
        value = int(raw)
    except (TypeError, ValueError):
        errors.append(f"{key.replace('-', ' ').title()} must be a whole number.")
        return default
    if not minimum <= value <= maximum:
        errors.append(f"{key.replace('-', ' ').title()} must be between {minimum} and {maximum}.")
        return max(minimum, min(maximum, value))
    return value


def collect_character_sheet(formdata, caste):
    """Read the dynamic dot fields and enforce the supplied builder's point budgets."""
    errors = []
    priorities = {}
    attributes = {}
    abilities = {}
    specialties = {}
    virtues = {}

    for category in ATTRIBUTE_GROUPS:
        key = f"{category}-priority"
        priorities[category] = _int_value(formdata, key, 0, 0, 8, errors)
        if priorities[category] not in (4, 6, 8):
            errors.append(f"Choose a {category} priority of 8, 6, or 4 points.")
        spent = 0
        for attribute in ATTRIBUTE_GROUPS[category]:
            value = _int_value(formdata, attribute, 1, 1, 5, errors)
            attributes[attribute] = value
            spent += value - 1
        if spent > priorities[category]:
            errors.append(
                f"{category.title()} Attributes spend {spent} points, exceeding the {priorities[category]}-point priority."
            )

    if len(set(priorities.values())) != 3 or any(value == 0 for value in priorities.values()):
        errors.append("Physical, Social, and Mental priorities must be 8, 6, and 4, each used once.")

    favored = ABILITY_GROUPS.get(caste, [])
    ability_spent = 0
    for ability in ALL_ABILITIES:
        minimum = 1 if ability in favored else 0
        value = _int_value(formdata, ability, minimum, 0, 5, errors)
        if value < minimum:
            errors.append(f"{ability.replace('-', ' ').title()} is favored by {caste} and starts at 1 dot.")
            value = minimum
        abilities[ability] = value
        ability_spent += value - minimum
        specialty = (formdata.get(f"{ability}-specialty", "") or "").strip()
        if specialty:
            specialties[ability] = specialty[:80]
    if ability_spent > 20:
        errors.append(f"Abilities spend {ability_spent} points; the maximum is 20.")

    for virtue in VIRTUES:
        virtues[virtue] = _int_value(formdata, virtue, 1, 1, 5, errors)

    core = {
        "willpower": _int_value(formdata, "willpower", 5, 1, 10, errors),
        "essence": _int_value(formdata, "essence", 2, 1, 5, errors),
    }
    sheet = {
        "priorities": priorities,
        "attributes": attributes,
        "abilities": abilities,
        "specialties": specialties,
        "virtues": virtues,
        "core": core,
        "personal_motes": (formdata.get("personal-motes", "") or "")[:40],
        "peripheral_motes": (formdata.get("peripheral-motes", "") or "")[:40],
        "backgrounds": (formdata.get("backgrounds", "") or "")[:4000],
    }
    return sheet, errors


def editor_data_from_character(character):
    if character is None:
        return {}
    data = dict(character.sheet or {})
    data.update(
        {
            "name": character.name,
            "player_name": character.player_name,
            "caste": character.caste,
            "concept": character.concept,
            "nature": character.nature,
            "anima": character.anima,
        }
    )
    return data


def editor_data_from_form(formdata):
    """Preserve submitted values if server-side character validation fails."""
    caste = formdata.get("caste", "Dawn")
    sheet, _ = collect_character_sheet(formdata, caste)
    data = dict(sheet)
    data.update(
        {
            "name": formdata.get("name", ""),
            "player_name": formdata.get("player_name", ""),
            "caste": caste,
            "concept": formdata.get("concept", ""),
            "nature": formdata.get("nature", ""),
            "anima": formdata.get("anima", ""),
        }
    )
    return data


def _campaign_membership(campaign_id):
    campaign = db.get_or_404(Campaign, campaign_id)
    membership = CampaignMembership.query.filter_by(
        campaign_id=campaign.id, user_id=current_user.id
    ).first()
    if membership is None:
        abort(403)
    return campaign, membership


def _require_storyteller(membership):
    if not membership.is_storyteller:
        abort(403)


def _populate_character_choices(form):
    characters = Character.query.filter_by(owner_id=current_user.id).order_by(Character.name).all()
    form.character_id.choices = [(0, "Join without a character yet")] + [
        (character.id, f"{character.name} ({character.caste})") for character in characters
    ]


@main.before_app_request
def log_request_start():
    if request.endpoint and not request.endpoint.startswith("static"):
        current_app.logger.debug("Request %s %s", request.method, request.path)


@main.route("/")
def home():
    return render_template("home.html")


@main.route("/mechanics")
def mechanics():
    return render_template("mechanics.html")


@main.route("/map")
def map_page():
    return render_template("map.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        existing = User.query.filter(or_(User.username.ilike(username), User.email == email)).first()
        if existing:
            flash("That username or email is already registered.", "warning")
        else:
            user = User(username=username, email=email)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            current_app.logger.info("Account created: user_id=%s", user.id)
            login_user(user)
            flash("Your legend begins. Welcome to Creation.", "success")
            return redirect(url_for("main.dashboard"))
    return render_template("auth/register.html", form=form)


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        identity = form.identity.data.strip()
        user = User.query.filter(
            or_(User.username.ilike(identity), User.email == identity.lower())
        ).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            current_app.logger.info("User signed in: user_id=%s", user.id)
            next_page = request.args.get("next")
            # Only allow local paths as redirect targets.
            if next_page and next_page.startswith("/") and not next_page.startswith("//"):
                return redirect(next_page)
            return redirect(url_for("main.dashboard"))
        flash("The credentials were not recognized.", "danger")
    return render_template("auth/login.html", form=form)


@main.route("/logout", methods=["POST"])
@login_required
def logout():
    current_app.logger.info("User signed out: user_id=%s", current_user.id)
    logout_user()
    flash("You have left Creation. Until next time.", "info")
    return redirect(url_for("main.home"))


@main.route("/dashboard")
@login_required
def dashboard():
    characters = Character.query.filter_by(owner_id=current_user.id).order_by(Character.updated_at.desc()).limit(5).all()
    memberships = CampaignMembership.query.filter_by(user_id=current_user.id).all()
    campaigns = [membership.campaign for membership in memberships]
    campaigns.sort(key=lambda item: item.created_at, reverse=True)
    upcoming_sessions = (
        SessionRecord.query.join(CampaignMembership, SessionRecord.campaign_id == CampaignMembership.campaign_id)
        .filter(CampaignMembership.user_id == current_user.id, SessionRecord.status == "planned")
        .order_by(SessionRecord.scheduled_at.asc().nullslast())
        .limit(5)
        .all()
    )
    return render_template(
        "dashboard.html", characters=characters, campaigns=campaigns, upcoming_sessions=upcoming_sessions
    )


@main.route("/characters")
@login_required
def characters():
    owned = Character.query.filter_by(owner_id=current_user.id).order_by(Character.updated_at.desc()).all()
    return render_template("characters/list.html", characters=owned)


@main.route("/characters/new", methods=["GET", "POST"])
@login_required
def new_character():
    form = CharacterForm()
    if request.method == "GET":
        form.player_name.data = current_user.username
    if form.validate_on_submit():
        sheet, errors = collect_character_sheet(request.form, form.caste.data)
        if errors:
            for error in errors:
                flash(error, "warning")
        else:
            character = Character(
                owner_id=current_user.id,
                name=form.name.data.strip(),
                player_name=form.player_name.data.strip(),
                caste=form.caste.data,
                concept=form.concept.data or "",
                nature=form.nature.data or "",
                anima=form.anima.data or "",
                sheet=sheet,
            )
            db.session.add(character)
            db.session.commit()
            current_app.logger.info("Character created: character_id=%s owner_id=%s", character.id, current_user.id)
            flash(f"{character.name} has been inscribed in the records.", "success")
            return redirect(url_for("main.character_detail", character_id=character.id))
    initial_data = (
        editor_data_from_form(request.form)
        if request.method == "POST"
        else {"player_name": current_user.username, "caste": "Dawn"}
    )
    return render_template("characters/form.html", form=form, character=None, sheet_data=initial_data)


@main.route("/characters/<int:character_id>")
@login_required
def character_detail(character_id):
    character = Character.query.filter_by(id=character_id, owner_id=current_user.id).first_or_404()
    return render_template("characters/detail.html", character=character)


@main.route("/characters/<int:character_id>/edit", methods=["GET", "POST"])
@login_required
def edit_character(character_id):
    character = Character.query.filter_by(id=character_id, owner_id=current_user.id).first_or_404()
    form = CharacterForm(obj=character)
    if form.validate_on_submit():
        sheet, errors = collect_character_sheet(request.form, form.caste.data)
        if errors:
            for error in errors:
                flash(error, "warning")
        else:
            character.name = form.name.data.strip()
            character.player_name = form.player_name.data.strip()
            character.caste = form.caste.data
            character.concept = form.concept.data or ""
            character.nature = form.nature.data or ""
            character.anima = form.anima.data or ""
            character.sheet = sheet
            db.session.commit()
            current_app.logger.info("Character updated: character_id=%s owner_id=%s", character.id, current_user.id)
            flash("Character sheet updated.", "success")
            return redirect(url_for("main.character_detail", character_id=character.id))
    sheet_data = editor_data_from_form(request.form) if request.method == "POST" else editor_data_from_character(character)
    return render_template("characters/form.html", form=form, character=character, sheet_data=sheet_data)


@main.route("/characters/<int:character_id>/delete", methods=["POST"])
@login_required
def delete_character(character_id):
    character = Character.query.filter_by(id=character_id, owner_id=current_user.id).first_or_404()
    name = character.name
    db.session.delete(character)
    db.session.commit()
    current_app.logger.info("Character deleted: character_id=%s owner_id=%s", character_id, current_user.id)
    flash(f"{name} was removed from your character records.", "info")
    return redirect(url_for("main.characters"))


@main.route("/campaigns")
@login_required
def campaigns():
    memberships = CampaignMembership.query.filter_by(user_id=current_user.id).all()
    campaign_list = [membership.campaign for membership in memberships]
    campaign_list.sort(key=lambda item: item.created_at, reverse=True)
    join_form = JoinCampaignForm()
    _populate_character_choices(join_form)
    return render_template("campaigns/list.html", campaigns=campaign_list, join_form=join_form)


@main.route("/campaigns/new", methods=["GET", "POST"])
@login_required
def new_campaign():
    form = CampaignForm()
    if form.validate_on_submit():
        campaign = Campaign(
            owner_id=current_user.id,
            name=form.name.data.strip(),
            description=form.description.data or "",
            setting_location=form.setting_location.data.strip(),
        )
        db.session.add(campaign)
        db.session.flush()
        membership = CampaignMembership(campaign=campaign, user=current_user, role="storyteller")
        db.session.add(membership)
        db.session.commit()
        current_app.logger.info("Campaign created: campaign_id=%s owner_id=%s", campaign.id, current_user.id)
        flash("Campaign created. Share its invitation code with your players.", "success")
        return redirect(url_for("main.campaign_detail", campaign_id=campaign.id))
    return render_template("campaigns/form.html", form=form, campaign=None)


@main.route("/campaigns/join", methods=["POST"])
@login_required
def join_campaign():
    form = JoinCampaignForm()
    _populate_character_choices(form)
    if form.validate_on_submit():
        code = form.invite_code.data.strip().upper()
        campaign = Campaign.query.filter_by(invite_code=code).first()
        if not campaign:
            flash("That invitation code was not found.", "danger")
        elif CampaignMembership.query.filter_by(campaign_id=campaign.id, user_id=current_user.id).first():
            flash("You are already part of that campaign.", "info")
        else:
            character = None
            if form.character_id.data:
                character = Character.query.filter_by(id=form.character_id.data, owner_id=current_user.id).first()
                if character is None:
                    abort(400)
            db.session.add(
                CampaignMembership(campaign=campaign, user=current_user, character=character, role="player")
            )
            db.session.commit()
            current_app.logger.info("User joined campaign: campaign_id=%s user_id=%s", campaign.id, current_user.id)
            flash(f"You joined {campaign.name}.", "success")
            return redirect(url_for("main.campaign_detail", campaign_id=campaign.id))
    else:
        for field_errors in form.errors.values():
            for error in field_errors:
                flash(error, "warning")
    return redirect(url_for("main.campaigns"))


@main.route("/campaigns/<int:campaign_id>")
@login_required
def campaign_detail(campaign_id):
    campaign, membership = _campaign_membership(campaign_id)
    session_form = SessionForm()
    npc_form = NPCForm()
    roll_form = DiceRollForm()
    character_form = CharacterSelectForm()
    owned_characters = Character.query.filter_by(owner_id=current_user.id).order_by(Character.name).all()
    character_form.character_id.choices = [(0, "No character assigned")] + [
        (character.id, f"{character.name} ({character.caste})") for character in owned_characters
    ]
    if membership.character_id:
        character_form.character_id.data = membership.character_id
    latest_rolls = RollRecord.query.filter_by(campaign_id=campaign.id).order_by(RollRecord.created_at.desc()).limit(8).all()
    return render_template(
        "campaigns/detail.html",
        campaign=campaign,
        membership=membership,
        session_form=session_form,
        npc_form=npc_form,
        roll_form=roll_form,
        character_form=character_form,
        latest_rolls=latest_rolls,
    )


@main.route("/campaigns/<int:campaign_id>/character", methods=["POST"])
@login_required
def update_campaign_character(campaign_id):
    campaign, membership = _campaign_membership(campaign_id)
    form = CharacterSelectForm()
    owned_characters = Character.query.filter_by(owner_id=current_user.id).order_by(Character.name).all()
    form.character_id.choices = [(0, "No character assigned")] + [
        (character.id, f"{character.name} ({character.caste})") for character in owned_characters
    ]
    if form.validate_on_submit():
        character = None
        if form.character_id.data:
            character = Character.query.filter_by(
                id=form.character_id.data, owner_id=current_user.id
            ).first()
            if character is None:
                abort(400)
        membership.character = character
        db.session.commit()
        current_app.logger.info(
            "Campaign character assignment updated: campaign_id=%s user_id=%s character_id=%s",
            campaign.id, current_user.id, character.id if character else None
        )
        flash("Your campaign character has been updated.", "success")
    else:
        flash("Could not update the campaign character. Please select one of your own sheets.", "warning")
    return redirect(url_for("main.campaign_detail", campaign_id=campaign.id))


@main.route("/campaigns/<int:campaign_id>/edit", methods=["GET", "POST"])
@login_required
def edit_campaign(campaign_id):
    campaign, membership = _campaign_membership(campaign_id)
    _require_storyteller(membership)
    form = CampaignForm(obj=campaign)
    if form.validate_on_submit():
        campaign.name = form.name.data.strip()
        campaign.setting_location = form.setting_location.data.strip()
        campaign.description = form.description.data or ""
        db.session.commit()
        current_app.logger.info("Campaign updated: campaign_id=%s", campaign.id)
        flash("Campaign details updated.", "success")
        return redirect(url_for("main.campaign_detail", campaign_id=campaign.id))
    return render_template("campaigns/form.html", form=form, campaign=campaign)


@main.route("/campaigns/<int:campaign_id>/delete", methods=["POST"])
@login_required
def delete_campaign(campaign_id):
    campaign, membership = _campaign_membership(campaign_id)
    _require_storyteller(membership)
    campaign_id = campaign.id
    db.session.delete(campaign)
    db.session.commit()
    current_app.logger.warning("Campaign deleted: campaign_id=%s by_user_id=%s", campaign_id, current_user.id)
    flash("Campaign and its sessions were deleted.", "info")
    return redirect(url_for("main.campaigns"))


@main.route("/campaigns/<int:campaign_id>/sessions/new", methods=["POST"])
@login_required
def new_session(campaign_id):
    campaign, membership = _campaign_membership(campaign_id)
    _require_storyteller(membership)
    form = SessionForm()
    if form.validate_on_submit():
        session_record = SessionRecord(
            campaign=campaign,
            created_by=current_user,
            title=form.title.data.strip(),
            scheduled_at=form.scheduled_at.data,
            summary=form.summary.data or "",
        )
        db.session.add(session_record)
        db.session.commit()
        current_app.logger.info("Session created: session_id=%s campaign_id=%s", session_record.id, campaign.id)
        flash("The next session has been added to the chronicle.", "success")
    else:
        for field_errors in form.errors.values():
            for error in field_errors:
                flash(error, "warning")
    return redirect(url_for("main.campaign_detail", campaign_id=campaign.id))


@main.route("/sessions/<int:session_id>", methods=["GET", "POST"])
@login_required
def session_detail(session_id):
    session_record = db.get_or_404(SessionRecord, session_id)
    campaign, membership = _campaign_membership(session_record.campaign_id)
    note_form = SessionNoteForm()
    roll_form = DiceRollForm()
    if note_form.validate_on_submit():
        visibility = note_form.visibility.data
        if not membership.is_storyteller:
            visibility = "party"
        note = SessionNote(
            session=session_record,
            author=current_user,
            content=note_form.content.data.strip(),
            visibility=visibility,
        )
        db.session.add(note)
        db.session.commit()
        current_app.logger.info("Session note added: session_id=%s user_id=%s", session_record.id, current_user.id)
        flash("Your note has been added.", "success")
        return redirect(url_for("main.session_detail", session_id=session_record.id))

    visible_notes = [
        note for note in session_record.notes
        if note.visibility == "party" or membership.is_storyteller or note.author_id == current_user.id
    ]
    rolls = RollRecord.query.filter_by(session_id=session_record.id).order_by(RollRecord.created_at.desc()).limit(20).all()
    return render_template(
        "sessions/detail.html",
        session_record=session_record,
        campaign=campaign,
        membership=membership,
        note_form=note_form,
        roll_form=roll_form,
        notes=visible_notes,
        rolls=rolls,
    )


@main.route("/campaigns/<int:campaign_id>/npcs", methods=["POST"])
@login_required
def add_npc(campaign_id):
    campaign, membership = _campaign_membership(campaign_id)
    _require_storyteller(membership)
    form = NPCForm()
    if form.validate_on_submit():
        npc = NPC(
            campaign=campaign,
            name=form.name.data.strip(),
            role=form.role.data or "",
            description=form.description.data or "",
        )
        db.session.add(npc)
        db.session.commit()
        current_app.logger.info("NPC added: npc_id=%s campaign_id=%s", npc.id, campaign.id)
        flash(f"{npc.name} added to the Storyteller's cast.", "success")
    else:
        for field_errors in form.errors.values():
            for error in field_errors:
                flash(error, "warning")
    return redirect(url_for("main.campaign_detail", campaign_id=campaign.id))


def _perform_roll(form, campaign, session_record=None):
    """Roll d10s using the success and botch rules documented on the supplied mechanics page."""
    pool = form.pool.data
    difficulty = form.difficulty.data
    roll_type = form.roll_type.data
    dice = [secrets.randbelow(10) + 1 for _ in range(pool)]
    successes = sum(1 if die == 10 and roll_type == "damage" else 2 if die == 10 else 1 for die in dice if die >= 7)
    is_botch = successes == 0 and 1 in dice
    succeeded = successes >= difficulty
    record = RollRecord(
        campaign=campaign,
        session=session_record,
        user=current_user,
        pool=pool,
        difficulty=difficulty,
        roll_type=roll_type,
        dice=dice,
        successes=successes,
        is_botch=is_botch,
        succeeded=succeeded,
    )
    db.session.add(record)
    db.session.commit()
    current_app.logger.info(
        "Dice roll: roll_id=%s campaign_id=%s user_id=%s pool=%s successes=%s botch=%s",
        record.id, campaign.id, current_user.id, pool, successes, is_botch
    )
    return record


@main.route("/campaigns/<int:campaign_id>/roll", methods=["POST"])
@login_required
def campaign_roll(campaign_id):
    campaign, _membership = _campaign_membership(campaign_id)
    form = DiceRollForm()
    if form.validate_on_submit():
        record = _perform_roll(form, campaign)
        if record.is_botch:
            flash(f"Botch! Dice: {', '.join(map(str, record.dice))}.", "danger")
        elif record.succeeded:
            flash(f"Success: {record.successes} successes. Dice: {', '.join(map(str, record.dice))}.", "success")
        else:
            flash(f"Failure: {record.successes} successes (difficulty {record.difficulty}). Dice: {', '.join(map(str, record.dice))}.", "warning")
    else:
        flash("Check the dice pool (0–50) and difficulty (1–10).", "warning")
    return redirect(url_for("main.campaign_detail", campaign_id=campaign.id))


@main.route("/sessions/<int:session_id>/roll", methods=["POST"])
@login_required
def session_roll(session_id):
    session_record = db.get_or_404(SessionRecord, session_id)
    campaign, _membership = _campaign_membership(session_record.campaign_id)
    form = DiceRollForm()
    if form.validate_on_submit():
        record = _perform_roll(form, campaign, session_record=session_record)
        if record.is_botch:
            flash(f"Botch! Dice: {', '.join(map(str, record.dice))}.", "danger")
        elif record.succeeded:
            flash(f"Success: {record.successes} successes. Dice: {', '.join(map(str, record.dice))}.", "success")
        else:
            flash(f"Failure: {record.successes} successes (difficulty {record.difficulty}).", "warning")
    else:
        flash("Check the dice pool (0–50) and difficulty (1–10).", "warning")
    return redirect(url_for("main.session_detail", session_id=session_record.id))


@main.route("/sessions/<int:session_id>/status", methods=["POST"])
@login_required
def toggle_session_status(session_id):
    session_record = db.get_or_404(SessionRecord, session_id)
    campaign, membership = _campaign_membership(session_record.campaign_id)
    _require_storyteller(membership)
    session_record.status = "completed" if session_record.status == "planned" else "planned"
    db.session.commit()
    current_app.logger.info("Session status changed: session_id=%s status=%s", session_record.id, session_record.status)
    flash("Session status updated.", "success")
    return redirect(url_for("main.session_detail", session_id=session_record.id))
