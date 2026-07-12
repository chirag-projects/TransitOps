#!/bin/bash


cd backend
source venv/bin/activate
uvicorn app:app --reload --host 0.0.0.0 --port 5678 >> app.log 2>&1
