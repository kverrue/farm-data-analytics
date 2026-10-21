# Farm Data Analytics

University group project: a Flask web application for exploring livestock and calving records using a SQLite database and interactive charts.

## Tech stack

- Python / Flask
- SQLite / SQL
- HTML, CSS / W3.CSS
- Chart.js

## Features

- Visualizations of livestock mortality and calving statistics
- Analysis of stillbirths by month
- Statistics on calvings over time and across animal families
- SQL database with relational tables for animals, families, calvings, and complications

## Run locally

```bash
cd site
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install 'Flask>=1.1,<2.0'
python -m flask --app flaskr init-db
python -m flask --app flaskr run
```

**Note:** This is a legacy university project originally developed with Flask 1.1 and Python 3.9. The setup above has not been verified on modern Python versions; dependency upgrades may be needed. Initialization overwrites/recreates the local instance database.

## Project structure

- `site/flaskr/index.py`: data queries and route rendering
- `site/flaskr/db.py`: database initialization and connections
- `site/flaskr/sql/`: schema and example SQL data
- `site/flaskr/templates/index.html`: Chart.js dashboard

## Project context

Developed collaboratively as part of a university assignment.
