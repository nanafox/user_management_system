from datetime import datetime, timezone
from uuid import uuid4

import sqlalchemy
from sqlalchemy import TIMESTAMP, Boolean, String, text
from sqlalchemy.orm import Mapped, Session, mapped_column

from ums import database
from ums.database import Base


class BaseModel:
    """Base model."""

    id: Mapped[sqlalchemy.Uuid] = mapped_column(
        sqlalchemy.Uuid,
        primary_key=True,
        default=uuid4,
        unique=True,
        index=True,
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        onupdate=datetime.now(timezone.utc),
    )

    def save(self, *, db: Session):
        """Saves the current object to the database."""
        return database.save(self, db=db)

    def delete(self, *, db: Session):
        """Deletes the current object from the database."""
        database.delete(self, db=db)

    def update(self, db: Session, **kwargs):
        """Updates the current object in the database."""
        for key, value in kwargs.items():
            setattr(self, key, value)

        return self.save(db=db)


class User(Base, BaseModel):
    """Model for users."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(20), index=True, unique=True)
    password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __str__(self):
        """Returns the username of the current user."""
        return self.username
