from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from passlib.context import CryptContext
from ums.config import settings


def hash_password(password: str):
    """Hashes a password."""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


SQLALCHEMY_DATABASE_URL = (
    "postgresql://"
    f"{settings.db_user}:{settings.db_password}@"
    f"{settings.db_host}:{settings.db_port}/{settings.db_name}"
)


engine = create_engine(SQLALCHEMY_DATABASE_URL)

DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Yields a database connection for ORM transactions."""
    db = DBSession()
    try:
        yield db
    finally:
        db.close()


def save(model_instance, *, db: Session):
    """Saves an instance of any object to the database."""
    if (
        hasattr(model_instance, "password")
        and model_instance.password is not None
    ):
        model_instance.password = hash_password(model_instance.password)
    db.add(model_instance)
    db.commit()
    db.refresh(model_instance)

    return model_instance


def delete(model_instance, *, db: Session):
    """Delete an instance of an object from the database."""
    db.delete(model_instance)
    db.commit()
