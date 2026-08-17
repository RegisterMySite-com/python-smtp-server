#!/bin/bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scrip>
pip install -r requirements.txt
python server.py