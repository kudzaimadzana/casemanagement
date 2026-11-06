"""Gunicorn entrypoint: ``gunicorn -c docker/gunicorn.conf.py wsgi:app``."""

from app import create_app

app = create_app()
