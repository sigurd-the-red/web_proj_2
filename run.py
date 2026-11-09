"""Local development entry point. Production WSGI imports `app` from this file."""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
