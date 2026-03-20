#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python scripts/init_db.py
python scripts/generate_sample_data.py
