import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# En Docker la URL llega por la variable de entorno DATABASE_URL (ver docker-compose.yml).
# El valor por defecto sirve para ejecutar la app fuera de Docker contra un PostgreSQL local.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://delivery_user:delivery_password@localhost:5432/delivery_db",
)

# init.sql crea las tablas dentro del esquema "delivery"; con este search_path
# SQLAlchemy las encuentra ahí en lugar de crear tablas duplicadas en "public".
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"options": "-csearch_path=delivery,public"},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependencia de FastAPI: abre una sesión por petición y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
