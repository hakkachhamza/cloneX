import shutil
from pathlib import Path

from app.config import get_settings

settings = get_settings()


def get_project_storage_path(project_id: str) -> Path:
    base = Path(settings.storage_local_path)
    return base / project_id


def delete_project_storage(storage_path: str) -> None:
    try:
        path = Path(storage_path)
        if path.exists():
            shutil.rmtree(path)
    except Exception:
        pass
