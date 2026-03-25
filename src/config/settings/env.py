import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]


def load_env_file() -> None:
    """
    Carga un archivo `.env` sencillo sin agregar dependencias extra.
    El objetivo es mantener bootstrap predecible incluso en contenedores minimalistas.
    """

    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def get_env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)


def get_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    return int(value) if value is not None else default


def get_list(name: str, default: list[str] | None = None) -> list[str]:
    value = os.environ.get(name)
    if value is None:
        return default or []
    return [item.strip() for item in value.split(",") if item.strip()]


load_env_file()

