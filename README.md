# Exalted Chronicle — Exalted 1st Edition Campaign Manager

A Flask web application based on the group's original Exalted 1E website. It keeps the original dark, gold-accented visual language and the supplied lore, mechanics, Solar character-builder categories, and Creation map locations, while adding accounts, persisted character sheets, campaigns, Storyteller tools, session records, notes, NPCs, and a d10 roller.

> **Before submitting:** complete the group information and team task division below. The group/member names and actual GitHub/PythonAnywhere URLs were not included in the supplied files, so they are intentionally left as placeholders rather than invented.

## Group and contribution division

- **Group name:** `[FILL IN GROUP NAME]`
- **Members and implementation responsibilities:**
  - `[MEMBER 1]` — `[TASKS / CONTRIBUTIONS]`
  - `[MEMBER 2]` — `[TASKS / CONTRIBUTIONS]`
  - `[MEMBER 3]` — `[TASKS / CONTRIBUTIONS]`
  - `[ADD OR REMOVE MEMBERS AS NEEDED]`
- **Application:** Exalted Chronicle — Exalted 1st Edition
- **Deployment:** `[ADD PYTHONANYWHERE APPLICATION URL]`
- **Source code:** `[ADD GITHUB REPOSITORY URL]`

Update this section to reflect the real group and each member's work before delivery.

## Features

### Public reference pages

- **Lore:** retains the supplied history article, covering the Primordial Age, the Primordial War, the First Age, the Age of Bronze, and the return of the Solars.
- **Mechanics:** retains the supplied explanation of the Storyteller and players, character creation, scenes, d10 pools, successes, botches, Willpower, Virtues, and stunts.
- **Map of Creation:** retains the seven supplied location markers and descriptions. The original `assets/exalted_map.jpeg` was not part of the uploaded files, so the project includes an original schematic SVG map background. Replace `app/static/assets/creation-map.svg` with an appropriately licensed map if the group has the original image.

### User accounts and character sheets

- Register, sign in, and sign out. Passwords are stored as password hashes.
- Create, view, edit, and delete Solar character sheets.
- Character sheets store the Caste, concept, Nature, Anima, Physical/Social/Mental Attributes, Abilities, specialties, Virtues, Willpower, Essence, motes, and backgrounds.
- The browser provides live point-spend feedback. The server independently validates submitted values and point budgets, so bypassing JavaScript does not bypass the rules enforced by the application.
- Attribute priorities must use 8, 6, and 4 points exactly once. Attribute dots range from 1 to 5. The five Caste-favored Abilities receive a starting dot; up to 20 additional Ability dots can be distributed. Abilities range from 0 to 5. Willpower ranges from 1 to 10, Essence from 1 to 5, and Virtues from 1 to 5.

### Campaign and Storyteller tools

- Create a campaign; its creator becomes the Storyteller.
- Invite players using the campaign's unique invitation code.
- Players can join with one of their own characters or join before choosing a character, then update their campaign character later from the campaign page.
- The Storyteller can edit or delete their campaign, schedule sessions, and maintain campaign NPCs.
- Every participant can open campaign sessions and add party-visible notes. The Storyteller can also add private notes visible only to the Storyteller.
- Campaign and session pages include a persistent d10 roller. Rolls are saved in the campaign/session record.

## Assignment requirements checklist

| Requirement | Implementation |
|---|---|
| At least 5 routes | More than 20 routes covering reference pages, authentication, characters, campaigns, sessions, NPCs, and dice rolls |
| At least 3 models | 8 models: `User`, `Character`, `Campaign`, `CampaignMembership`, `SessionRecord`, `SessionNote`, `NPC`, and `RollRecord` |
| At least 2 forms | 10 Flask-WTF forms: registration, login, character, campaign, join campaign, character selection, session, session note, NPC, and dice roller |
| Debug / information logging | Python logging with a rotating file at `instance/logs/exalted.log`; request paths are logged at DEBUG level and important changes at INFO/WARNING |
| Persistent storage | Flask-SQLAlchemy with SQLite by default |

## Technology

- Python and Flask
- Jinja2 templates
- Flask-WTF and WTForms (including CSRF protection)
- Flask-Login
- Flask-SQLAlchemy / SQLAlchemy
- SQLite by default; another SQLAlchemy-supported database can be configured with `DATABASE_URL`
- python-dotenv for environment configuration
- Bootstrap 5, Leaflet, and the original custom CSS/JavaScript builder

## Application organization

```text
exalted-flask/
├── app/
│   ├── __init__.py              # Flask application factory, extension setup, logging
│   ├── extensions.py            # SQLAlchemy and Flask-Login instances
│   ├── forms.py                 # Flask-WTF forms
│   ├── models.py                # User, Character, Campaign, Membership, Session, NPC, Note, Roll
│   ├── routes.py                # HTTP routes, permissions, validation, dice logic
│   ├── templates/
│   │   ├── base.html            # Shared navigation, flashes, footer
│   │   ├── home.html            # Supplied Exalted history/lore page
│   │   ├── mechanics.html       # Supplied mechanics page
│   │   ├── map.html             # Interactive Creation map
│   │   ├── dashboard.html       # Signed-in user's overview
│   │   ├── auth/                # Login and registration
│   │   ├── characters/          # Character list, builder, character detail
│   │   ├── campaigns/           # Campaign list, form, Storyteller dashboard
│   │   └── sessions/            # Session details, notes, and roll history
│   └── static/
│       ├── css/styles.css       # Supplied theme plus application components
│       ├── js/character.js      # Caste bonuses and client-side dot allocation
│       ├── js/map.js            # Leaflet markers and location popups
│       └── assets/creation-map.svg # Local map background; replaceable asset
├── instance/                    # Local SQLite database and log directory at runtime
├── tests/test_app.py            # Basic application and account-flow tests
├── config.py                    # Environment-based configuration
├── run.py                       # Local entry point and WSGI import target
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
└── README.md
```

## Installation and local execution

Python 3.10 or newer is recommended.

1. Create and enter a virtual environment:

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   # macOS / Linux
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create your environment file and set a secret key:

   ```bash
   cp .env.example .env
   ```

   On Windows, copy `.env.example` to `.env` using File Explorer or `Copy-Item .env.example .env`.

4. Run the application:

   ```bash
   python run.py
   ```

5. Open `http://127.0.0.1:5000`.

The SQLite database is created automatically at `instance/exalted.db` on first startup. Application logs are written to `instance/logs/exalted.log` and rotated after reaching the configured size. Debug-level request messages are available when Flask debug logging is enabled.

## User guide

### 1. Create an account

Open **Join the Chronicle**, provide a username, email, and password, then submit the registration form. After registration the application signs you in and opens your dashboard.

### 2. Create a Solar character

Open **Characters → Create Solar**. Enter the character identity and choose one of the five Solar Castes. Select Physical, Social, and Mental priorities using 8, 6, and 4 points once each. Distribute Attribute dots within those budgets. The selected Caste determines the five favored Abilities, which start at one dot; distribute up to 20 more Ability dots. Enter specialties, Virtues, Willpower, Essence, motes, and backgrounds, then save. The server validates the submitted sheet before it is stored.

Open a saved sheet to review its values, edit it, or delete it.

### 3. Start a campaign as Storyteller

Open **Campaigns → Create campaign**, enter a name, starting location, and premise. The account that creates the campaign becomes its Storyteller. The campaign page displays a unique invitation code; share that code with your players.

The Storyteller can edit the campaign, schedule sessions, add NPCs, and record GM-only session notes.

### 4. Join a campaign as a player

Open **Campaigns**, enter the invitation code, and optionally select one of your character sheets. After joining, the campaign appears in your campaign hall and dashboard. Players can view session information, add party-visible notes, and use the campaign dice roller.

### 5. Run sessions and keep a chronicle

Open a campaign and select a session. The session page contains the date, session brief, notes, roll history, and a d10 roller. Players' notes are visible to the party. The Storyteller may choose **Storyteller only** for private preparation or secrets. The Storyteller can switch a session between planned and completed.

### 6. Roll dice

Choose a pool from 0 to 50 dice, a difficulty from 1 to 10, and either a standard or damage roll. For a standard roll, every 7–9 is one success and each 10 is two. For damage, a 10 counts as one success. A botch is recorded when a roll has no successes and at least one die shows 1. Every roll is stored and displayed in the campaign or session history.

## Routes / pages

The application provides more than the required five routes. Main pages include:

- `/` — lore / home
- `/mechanics` — rules reference
- `/map` — interactive map
- `/register`, `/login`, `/logout` — account access
- `/dashboard` — user dashboard
- `/characters`, `/characters/new`, `/characters/<id>`, `/characters/<id>/edit` — character management
- `/campaigns`, `/campaigns/new`, `/campaigns/<id>`, `/campaigns/<id>/edit`, `/campaigns/join` — campaigns
- `/campaigns/<id>/sessions/new`, `/sessions/<id>` — session management
- `/campaigns/<id>/npcs` — NPC management
- `/campaigns/<id>/roll`, `/sessions/<id>/roll` — dice rolls

## Deployment on PythonAnywhere

1. Push the project to the group's GitHub repository and create a PythonAnywhere account.
2. Open a Bash console on PythonAnywhere and clone the repository:

   ```bash
   git clone https://github.com/YOUR-GROUP/YOUR-REPOSITORY.git
   cd YOUR-REPOSITORY
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

3. Edit `.env` and set a long, random `SECRET_KEY`. Set `SESSION_COOKIE_SECURE=true` on the HTTPS PythonAnywhere deployment. Ensure the `instance/` directory is writable by the PythonAnywhere account. The default SQLite database will be located there.
4. In the PythonAnywhere **Web** tab, create a Flask web app using the Python version matching the virtual environment.
5. Set the virtualenv path to the repository's `.venv` directory.
6. Edit the WSGI configuration file and point it to the cloned repository. Example (replace the username and directory):

   ```python
   import sys
   project_home = '/home/YOUR_USERNAME/YOUR-REPOSITORY'
   if project_home not in sys.path:
       sys.path.insert(0, project_home)

   from run import app as application
   ```

7. Reload the web app from the PythonAnywhere **Web** tab and test registration, character creation, campaign creation, and a session roll.
8. Add the resulting application URL to the group submission and to the preamble above.

For an existing deployment, back up `instance/exalted.db` before replacing code or changing the schema. This project calls `db.create_all()` at startup for initial schema creation; it does not perform migrations. Use a migration tool such as Flask-Migrate/Alembic before making incompatible schema changes in a live database.

## Logging and tests

- Logs: `instance/logs/exalted.log` (rotating file handler).
- Run the basic tests after installing dependencies:

  ```bash
  pip install -r requirements-dev.txt
  pytest -q
  ```

The tests cover application initialization, account registration/login, character persistence, campaign creation, and the invitation-based membership workflow.

## Notes and limitations

- The supplied source is presented as Exalted 1st Edition. The character builder and dice roller implement the allocation and resolution rules explicitly represented in the supplied JavaScript and mechanics page; they are not a complete implementation of every rule in the tabletop books.
- The application is a campaign-management companion, not a full virtual tabletop. It does not yet provide grid combat, initiative automation, map drawing, live chat, file uploads, or real-time synchronization.
- The Storyteller's ability to create and manage a campaign is permission-checked on the server. Character sheets are private to their owner by default; choosing a character when joining a campaign links it to that campaign roster.
- The map image is a new schematic asset because the referenced JPEG was absent from the supplied files. The original seven location descriptions and marker coordinates were retained.
