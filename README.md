# Mansvi Blog ✿
Flask + SQLAlchemy + Flask-Migrate + Flask-Login + Flask-WTF.

## Run (Linux / macOS)
    python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    export FLASK_APP=wsgi.py
    flask db upgrade
    flask seed          # optional demo data (login: mansvi / mansvi123)
    python run.py       # http://127.0.0.1:5000

## Run (Windows PowerShell)
    py -m venv venv; venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    $env:FLASK_APP="wsgi.py"
    flask db upgrade; flask seed
    python run.py

## Tests:  python -m pytest -q
## Production: gunicorn --preload -w 3 -b 0.0.0.0:8000 wsgi:app
## Docker:  docker compose up --build   (http://localhost:8000)
