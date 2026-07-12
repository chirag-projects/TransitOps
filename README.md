# TransitOps

## Backend Setup

- Setup environment

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- Install dependencies

  ```bash
  pip3 install -r requirements.txt
  ```

- Running the backend server

  ```bash
  bash run.sh
  ```

  - logs will be present in backend/app.log file

* Run without run script

  ```bash
  uvicorn app:app --reload --host 0.0.0.0 --port 5678
  ```

  - The API documentation will be available at http://localhost:5678/docs

* Create base admin user.

  ```bash
  cd backend && python3 - <<'PY'
  from model.dao import seed_admin
  seed_admin()
  print('seed_admin() complete')
  PY
  ```
