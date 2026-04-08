# SkyFinance Dashboard

This version of the project is intentionally minimal:

- `app.py` contains the full FastAPI app, data loading, filters, summaries, and Plotly chart generation.
- `templates/app.html` is the single Jinja template used by every page.
- `static/css/style.css` keeps the existing dark dashboard look.

The data shown, the layout, and the year/month filters are still preserved, but the old router-per-module API layer and the large frontend JavaScript file have been removed.

## Stack

- Python
- FastAPI
- Jinja2 templates
- Pandas
- Plotly
- PostgreSQL

## Run

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Open `http://localhost:8000`.

## Project Structure

```text
finance_dashboard_project/
|-- app.py
|-- requirements.txt
|-- README.md
|-- static/
|   `-- css/
|       `-- style.css
`-- templates/
    `-- app.html
```
