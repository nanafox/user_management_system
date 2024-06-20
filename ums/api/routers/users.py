from fastapi import APIRouter, status

from ums import schemas
from ums.api.deps import (
    DBSessionDependency,
    UserIdDependency,
    UsernameDependency,
)
from ums.crud import crud_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=schemas.UserResponse,
    response_description="User created successfully",
    summary="Create a user",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(db: DBSessionDependency, user: schemas.UserCreate):
    """Create a new user."""
    user_obj = crud_user.create(db=db, schema=user)
    return {
        "message": "User created successfully",
        "status_code": status.HTTP_201_CREATED,
        "data": user_obj,
    }


@router.get(
    "/{user_id}",
    response_model=schemas.UserResponse,
    response_description="User retrieved successfully",
    summary="Retrieve a user by their id",
)
async def get_user_by_id(
    db: DBSessionDependency,
    user_id: str = UserIdDependency,
):
    """Retrieve a user by their id."""
    user_obj = crud_user.get_by_id(db=db, user_id=user_id)
    return {
        "message": "User created successfully",
        "status_code": status.HTTP_201_CREATED,
        "data": user_obj,
    }


@router.get(
    "",
    response_model=schemas.UserResponse,
    response_description="User data retrieved successfully",
    summary="Retrieve all users or a user by their username",
)
async def get_users(
    db: DBSessionDependency,
    username: str = UsernameDependency,
    skip: int = 0,
    limit: int = 25,
):
    """
    This endpoint retrieves all users starting with the first 25 by default.
    If you want a specific user, you can specify their username as query when
    sending the request.

    Also, you can use the `skip` and `limit` to control the the number of
    users you receive for each request. At any point in time, you can only go
    up to 100 users per request.
    """
    if username:
        user_data = crud_user.get_by_username(username=username, db=db)
    else:
        user_data = crud_user.get_all(db=db, skip=skip, limit=limit)

    return {
        "message": "User data retrieval successful",
        "status_code": status.HTTP_200_OK,
        "data": user_data,
    }


@router.put(
    "/{user_id}",
    response_model=schemas.UserResponse,
    response_description="User updated successfully",
    summary="Update a user by their id",
)
async def update_user_by_id(
    db: DBSessionDependency,
    user: schemas.UserUpdate,
    user_id: str = UserIdDependency,
):
    """Update a user by their id."""
    updated_user = crud_user.update(
        db=db, user_id=user_id, schema=user, by="id"
    )
    return {
        "message": "User updated successfully",
        "status_code": status.HTTP_200_OK,
        "data": updated_user,
    }


@router.put(
    "",
    response_model=schemas.UserResponse,
    response_description="User updated successfully",
    summary="Update a user by their username",
)
async def update_user_by_username(
    db: DBSessionDependency,
    user: schemas.UserUpdate,
    username: str = UsernameDependency,
):
    """Update a user by their username."""
    updated_user = crud_user.update(
        db=db, user_id=username, schema=user, by="username"
    )
    return {
        "message": "User updated successfully",
        "status_code": status.HTTP_200_OK,
        "data": updated_user,
    }


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="User deleted successfully",
    summary="Delete a user by their id",
)
async def delete_user_by_id(
    db: DBSessionDependency, user_id: str = UserIdDependency
):
    """Delete a user by their id."""
    return crud_user.delete(user_id=user_id, db=db, by="id")


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="User deleted successfully",
    summary="Delete a user by their username",
)
async def delete_user_by_username(
    db: DBSessionDependency, username: str = UsernameDependency
):
    """Delete a user by their username."""
    return crud_user.delete(user_id=username, db=db, by="username")
