#!/bin/sh
python -c "from app import init_db; init_db()"
exec gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
