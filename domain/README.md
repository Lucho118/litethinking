# domain

Pure Python package containing **only** business entities and domain rules.

## Rules
- NO Django, FastAPI, SQLAlchemy, or any infrastructure import allowed here.
- Entities are plain Python dataclasses or classes.
- Installed as a local path dependency from `backend/` and `microservices/`.
