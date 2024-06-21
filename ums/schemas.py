from datetime import datetime
from typing import Any, Dict, Optional, Union
from uuid import UUID

from fastapi import status
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from ums.config import settings


def create_response_example(
    *,
    status_code: int,
    description: str,
    message: str,
    user_data: Union[dict, list],
) -> Dict[str, Any]:
    """Return a dictionary representing a user response schema."""
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": {
                        "message": message,
                        "status_code": status_code,
                        "data": user_data,
                    }
                }
            },
        }
    }


users_data = [
    {
        "username": "john_doe",
        "id": "ecb79dc4-d547-4ac4-aed0-a7ce6c84f805",
        "is_active": True,
        "created_at": "2024-06-21T15:22:58.844064Z",
        "updated_at": "2024-06-21T15:22:58.844064Z",
    },
    {
        "username": "bob",
        "id": "88492fdd-975f-4bba-a017-35f82978eb9b",
        "is_active": True,
        "created_at": "2024-06-21T15:22:18.728110Z",
        "updated_at": "2024-06-21T15:22:18.728110Z",
    },
]

users_retrieved_response = create_response_example(
    status_code=status.HTTP_200_OK,
    description="User data retrieved successfully",
    message="User data retrieval successful",
    user_data=users_data,
)

user_created_response = create_response_example(
    status_code=status.HTTP_201_CREATED,
    description="User created successfully",
    message="User created successfully",
    user_data=users_data[0],
)

user_retrieved_response = create_response_example(
    status_code=status.HTTP_200_OK,
    description="User data retrieved successfully",
    message="User data retrieval successful",
    user_data=users_data[0],
)

user_updated_response = create_response_example(
    status_code=status.HTTP_200_OK,
    message="User updated successfully",
    description="User updated successfully",
    user_data={
        "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
        "username": "jdoe_",
        "is_active": True,
        "created_at": "2021-07-01T12:01:56",
        "updated_at": "2021-09-01T04:12:04",
    },
)

user_not_found = {
    status.HTTP_404_NOT_FOUND: {
        "description": "User not found",
        "content": {
            "application/json": {"example": {"detail": "user not found"}}
        },
    }
}


unprocessable_entity = {
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "username"],
                            "msg": "Field required",
                            "input": {"password": "password1234"},
                        }
                    ]
                }
            }
        },
    }
}


class UserBase(BaseModel):
    """Schema for validating and creating users."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        revalidate_instances="always",
        json_schema_extra={
            "examples": [{"username": "john_doe", "password": "password1234"}]
        },
    )

    username: str = Field(..., min_length=3, max_length=15)

    @field_validator("username")
    @classmethod
    def username_must_not_be_numeric(cls, value):
        """
        Validates that the username field is not numeric.

        Args:
            value: The value of the username field to be validated.

        Returns:
            str: The validated username value.

        Raises:
            ValueError: If the username is numeric.

        Examples:
            >>> UserBase.username_must_not_be_numeric("john_doe")
            'john_doe'
            >>> UserBase.username_must_not_be_numeric("12345")
            Traceback (most recent call last):
            ...
            ValueError: username cannot be just numbers
        """

        if value.isnumeric():
            raise ValueError("username cannot be just numbers")
        return value


class UserCreate(UserBase):
    """
    A class representing the schema for creating a user.

    This class defines the schema for creating a user, including password
    constraints based on the minimum and maximum password lengths specified in
    the settings.

    - **username**: The username of the user.
    - **password**: The password of the user with length constraints.
    """

    password: str = Field(
        ...,
        min_length=settings.minimum_password_length,
        max_length=settings.maximum_password_length,
    )


class UserUpdate(UserBase):
    """
    A class representing the schema for updating a user.

    This class defines the schema for updating a user, allowing for optional
    password changes within the specified length constraints from the
    settings. The username is required for updating a user.

    - **username**: The username of the user.
    - **password**: An optional new password for the user with length
      constraints.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"username": "joe_", "password": "new_password"}]
        }
    )

    password: Optional[str] = Field(
        None,
        min_length=settings.minimum_password_length,
        max_length=settings.maximum_password_length,
    )


class User(UserBase):
    """
    A class representing the schema for a user entity.

    This class defines the schema for a user, including attributes like ID,
    active status, creation timestamp, and last update timestamp.

    - **id**: The unique identifier for the user.
    - **is_active**: A boolean indicating the user's active status.
    - **created_at**: The timestamp when the user was created.
    - **updated_at**: The timestamp when the user was last updated.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    """
    A class representing the response structure for user-related operations.

    This class defines the structure of a response for user operations,
    including a message, status code, and data payload.

    - **message**: A string message describing the response.
    - **status_code**: An integer representing the status code of the response.
    - **data**: The payload data included in the response.
    """

    message: str
    status_code: int
    data: Union[list[User], User]


class StatusResponse(BaseModel):
    """
    A class representing the response structure for status information.

    This class defines the structure of a response for status information,
    including a status string with a default value of "OK".

    - **status**: A string indicating the status information (default is "OK").
    """

    status: str = "OK"
