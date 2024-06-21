from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query, Session

from ums import models, schemas


class UserCrud:
    """A collection of methods for CRUD operation on the users endpoint."""

    def __init__(self, model: models.User = models.User):
        self.model = model
        self.model_name = model.__name__.lower()
        self.not_found_error = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{self.model_name} not found",
        )

    def get_by_id(self, *, user_id: str, db: Session) -> models.User:
        """
        Retrieves a user by their ID.

        Args:
            user_id (str): The ID of the user to retrieve
            db (Session): The database session instance

        Raises:
            HTTPException: Error 404 is raised if the user does not exist. In
            the event the ID provided is not valid, error 400 is raised.

        Returns:
            models.User: The user with the requested ID.
        """
        try:
            UUID(user_id)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"invalid {self.model_name} id",
            ) from error
        if user := db.get(self.model, user_id):
            return user

        raise self.not_found_error

    def get_by_username(self, *, username: str, db: Session) -> models.User:
        if user := db.query(self.model).filter_by(username=username).first():
            return user

        raise self.not_found_error

    def get_all(
        self, *, db: Session, skip: int = 0, limit: int = 25
    ) -> Query:
        """
        Retrieves all users, but the results are paginated.

        Args:
            db (Session): The database session instance
            skip (int, optional): The starting point for the data.
            Defaults to 0.
            limit (int, optional): The number of retrievable users.
            Defaults to 25.

        Returns:
            Query: The result of all users.
        """
        limit = min(limit, 100)
        return db.query(self.model).offset(skip).limit(limit)

    def __get_user(
        self, *, by: str, user_id: str, db: Session
    ) -> models.User:
        """
        Retrieves a user by their ID or username.

        Args:
            by (str): The type of data to use for the search.
            user_id (str): The ID or username of the user to retrieve
            db (Session): The database session instance

        Raises:
            HTTPException: Error 404 is raised if the user does not exist.

        Returns:
            models.User: The user with the requested ID or username.
        """
        match by:
            case "id":
                return self.get_by_id(user_id=user_id, db=db)
            case "username":
                return self.get_by_username(username=user_id, db=db)
            case _:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "message": "An error while performing this action",
                        "next_steps": "If the error persists, please contact "
                        "the system administrator.",
                    },
                )

    def create(
        self, *, db: Session, schema: schemas.UserCreate
    ) -> models.User:
        """
        Creates a new user.

        Args:
            db (Session): The database session instance
            schema (schemas.UserCreateUpdate): The user schema to use

        Raises:
            HTTPException: Error 409 (Conflict) is raised if the user to be
            created already exists.
        Returns:
            models.User: A new user instance.
        """
        try:
            return self.model(**schema.model_dump()).save(db=db)
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="user already exists",
            ) from e

    def update(
        self,
        *,
        db: Session,
        user_id: str,
        schema: schemas.UserUpdate,
        by: str,
    ) -> models.User:
        """
        Updates a user.

        Args:
            db (Session): The database session instance
            user_id (str): The ID of the user to update
            schema (schemas.UserCreateUpdate): The user schema to use

        Raises:
            HTTPException: Error 404 is raised if the user does not exist.

        Returns:
            models.User: The updated user instance.
        """
        user = self.__get_user(by=by, user_id=user_id, db=db)

        return user.update(**schema.model_dump(exclude_unset=True), db=db)

    def delete(self, *, db: Session, user_id: str, by: str) -> models.User:
        """
        Deletes a user.

        Args:
            db (Session): The database session instance
            user_id (str): The ID of the user to delete

        Raises:
            HTTPException: Error 404 is raised if the user does not exist.

        Returns:
            models.User: The deleted user instance.
        """
        user = self.__get_user(by=by, user_id=user_id, db=db)
        user.delete(db=db)


crud_user = UserCrud()
