from typing import Optional

from fastapi import APIRouter, Query, status

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
    summary="Create a user",
    status_code=status.HTTP_201_CREATED,
    responses={
        **schemas.user_created_response,
        **schemas.unprocessable_entity,
    },
    operation_id="create_user",
)
async def create_user(db: DBSessionDependency, user: schemas.UserCreate):
    """
    This API endpoint is responsible for creating a new user within the
    system. It accepts user data in the request body, i.e., `username` and
    `password`, and any additional profile information.
    """
    user_obj = crud_user.create(db=db, schema=user)
    return {
        "message": "User created successfully",
        "status_code": status.HTTP_201_CREATED,
        "data": user_obj,
    }


@router.get(
    "/{user_id}",
    response_model=schemas.UserResponse,
    summary="Retrieve a user by their id",
    responses={**schemas.user_retrieved_response, **schemas.user_not_found},
    operation_id="get_user_by_id",
)
async def get_user_by_id(
    db: DBSessionDependency,
    user_id: str = UserIdDependency,
):
    """
    This API endpoint retrieves a user from the system based on their unique
    user ID. It is designed to provide detailed user information by querying
    the database with the specified user ID.
    """
    user_obj = crud_user.get_by_id(db=db, user_id=user_id)
    return {
        "message": "User data retrieval successful",
        "status_code": status.HTTP_200_OK,
        "data": user_obj,
    }


@router.get(
    "",
    response_model=schemas.UserResponse,
    summary="Retrieve all users or a user by their username",
    responses={**schemas.users_retrieved_response, **schemas.user_not_found},
    operation_id="get_users",
)
async def get_users(
    db: DBSessionDependency,
    username: Optional[str] = Query(
        None, description="The username of the user"
    ),
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
    responses={
        **schemas.user_updated_response,
        **schemas.user_not_found,
        **schemas.unprocessable_entity,
    },
    operation_id="update_user_by_id",
)
async def update_user_by_id(
    db: DBSessionDependency,
    user: schemas.UserUpdate,
    user_id: str = UserIdDependency,
):
    """
    This endpoint updates a user by their id. The user id is a unique
    identifier for each user in the system. Pass the ID of the user you want
    to update and the new data you want to update the user with.

    For convenience, you can omit the `password` field if you don't want to
    update the user's password. You can simply pass the `username` field only
    and send the request. If do want to update the password, you can pass the
    `password` field along with the `username` field.
    """
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
    responses={
        **schemas.user_updated_response,
        **schemas.user_not_found,
        **schemas.unprocessable_entity,
    },
    operation_id="update_user_by_username",
)
async def update_user_by_username(
    db: DBSessionDependency,
    user: schemas.UserUpdate,
    username: str = UsernameDependency,
):
    """
    This endpoint updates a user by their username. The user username is a
    unique identifier for each user in the system. Pass the ID of the user you
    want to update and the new data you want to update the user with.

    For convenience, you can omit the `password` field if you don't want to
    update the user's password. You can simply pass the `username` field only
    and send the request. If do want to update the password, you can pass the
    `password` field along with the `username` field.
    """
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
    responses={**schemas.user_not_found},
    operation_id="delete_user_by_id",
)
async def delete_user_by_id(
    db: DBSessionDependency, user_id: str = UserIdDependency
):
    """
    This endpoint deletes a user by their id. This is a destructive operation
    and cannot be undone. Please be sure you want to delete the user before
    sending the request.
    """
    crud_user.delete(user_id=user_id, db=db, by="id")


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="User deleted successfully",
    summary="Delete a user by their username",
    responses={
        **schemas.user_not_found,
    },
    operation_id="delete_user_by_username",
)
async def delete_user_by_username(
    db: DBSessionDependency, username: str = UsernameDependency
):
    """
    This endpoint deletes a user by their username. This is a destructive
    operation and cannot be undone. Please be sure you want to delete the user
    before sending the request.
    """
    crud_user.delete(user_id=username, db=db, by="username")
