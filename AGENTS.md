# AGENT.md

## Project Name

**APALens** – APA Team and Player Stats Viewer

## Purpose

APALens is a Flask web application for visualizing statistics from the American Poolplayers Association (APA). It allows users to view team and player performance by fetching data from APA's backend services.

This tool is intended for use by APA players, team captains, and league operators who want quick insights into standings, performance trends, and player details.

## Features

- Display APA team stats by division and week  
- View team statistics, rankings, and win/loss history  

## Key Technologies

- Python 3.x  
- Flask  
- Requests (for API calls)  
- Jinja2 (templating)  
- Docker (optional for deployment)

## API Authentication

The application requires an APA `refresh_token` to retrieve data. This token must be passed via the environment variable:

```bash
export APA_REFRESH_TOKEN="your-apa-refresh-token"
```

The application automatically handles token refresh and session management when making requests to APA's backend.

## Project Structure

```bash
src/
├── app.py                # Flask app entry point
├── adapters.py           # HTTPS Adapter and GraphQL Adapter
├── templates/            # Jinja2 templates for rendering pages
├── static/               # Static CSS and JS
```

## Quickstart

### Local Setup

```bash
git clone https://github.com/Mattsface/apalens.git
cd apalens
pip install -e .

export APA_REFRESH_TOKEN="your-apa-refresh-token"
python -m flask run
```

### Docker

```bash
docker build -t apalens .
docker run -p 5000:5000 -e APA_REFRESH_TOKEN=your-apa-refresh-token apalens
```

Then open `http://localhost:5000` in your browser.

## Example Usage (for Codex)

```bash
# Run the web app
export APA_REFRESH_TOKEN=abc123
flask run
```
