#!/bin/sh
source .venv/bin/activate
python -m fastapi dev main.py --port $PORT