"""Smoke tests for the main account, character, and campaign workflows."""

import pytest

from app import create_app
from app.extensions import db
from app.models import Campaign, CampaignMembership, Character, User


@pytest.fixture()
def app():
    application = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SECRET_KEY": "test-secret",
        }
    )
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def register(client, username="solara", email="solara@example.com"):
    return client.post(
        "/register",
        data={
            "username": username,
            "email": email,
            "password": "radiant-password",
            "confirm_password": "radiant-password",
        },
        follow_redirects=True,
    )


def test_public_pages_load(client):
    assert client.get("/").status_code == 200
    assert client.get("/mechanics").status_code == 200
    assert client.get("/map").status_code == 200


def test_registration_and_dashboard(client):
    response = register(client)
    assert response.status_code == 200
    assert b"Welcome" in response.data or b"dashboard" in response.data.lower()
    assert client.get("/dashboard").status_code == 200


def test_login_logout(client):
    register(client)
    client.post("/logout", follow_redirects=True)
    response = client.post(
        "/login",
        data={"identity": "solara", "password": "radiant-password"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert client.get("/dashboard").status_code == 200


def test_owner_can_create_campaign_and_character(client, app):
    register(client)
    campaign_response = client.post(
        "/campaigns/new",
        data={"name": "The Sunless Throne", "setting_location": "The Imperial City", "description": "A test chronicle."},
        follow_redirects=True,
    )
    assert campaign_response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username="solara").one()
        campaign = Campaign.query.filter_by(name="The Sunless Throne").one()
        assert CampaignMembership.query.filter_by(campaign_id=campaign.id, user_id=user.id, role="storyteller").one()

        # A character sheet with 8/6/4 priorities and five Dawn caste dots.
        payload = {
            "name": "Ashen Dawn", "player_name": "solara", "caste": "Dawn",
            "concept": "Disgraced general", "nature": "Rebel", "anima": "A burning halo",
            "physical-priority": "8", "social-priority": "6", "mental-priority": "4",
            "strength": "3", "dexterity": "4", "stamina": "3",
            "charisma": "3", "manipulation": "3", "appearance": "3",
            "perception": "2", "intelligence": "2", "wits": "3",
            "archery": "1", "brawl": "1", "martial-arts": "1", "thrown": "1", "melee": "1",
            "willpower": "5", "essence": "2",
            "compassion": "1", "conviction": "1", "temperance": "1", "valor": "1",
        }
    response = client.post("/characters/new", data=payload, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        character = Character.query.filter_by(name="Ashen Dawn").one()
        assert character.sheet["attributes"]["dexterity"] == 4
        assert character.sheet["abilities"]["archery"] == 1


def test_invitation_code_join_flow(client, app):
    register(client, "storyteller", "storyteller@example.com")
    client.post(
        "/campaigns/new",
        data={"name": "The East Burns", "setting_location": "The East", "description": "A campaign."},
    )
    with app.app_context():
        campaign = Campaign.query.filter_by(name="The East Burns").one()
        invite_code = campaign.invite_code
    client.post("/logout")
    register(client, "player", "player@example.com")
    response = client.post(
        "/campaigns/join",
        data={"invite_code": invite_code, "character_id": "0"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        player = User.query.filter_by(username="player").one()
        campaign = Campaign.query.filter_by(name="The East Burns").one()
        assert CampaignMembership.query.filter_by(campaign_id=campaign.id, user_id=player.id, role="player").one()
