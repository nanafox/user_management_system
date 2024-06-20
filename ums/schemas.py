from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from ums.config import settings


class UserBase(BaseModel):
    """Schema for validating and creating users."""

    username: str = Field(..., min_length=3, max_length=15)


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

    Explanation:
    This class defines the schema for updating a user, allowing for optional
    password changes within the specified length constraints from the
    settings. The username is required for updating a user.

    - **username**: The username of the user.
    - **password**: An optional new password for the user with length
      constraints.
    """

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

    - *id*: The unique identifier for the user.
    - **is_active**: A boolean indicating the user's active status.
    - **created_at**: The timestamp when the user was created.
    - **updated_at**: The timestamp when the user was last updated.
    """

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


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

    Args:
    - **status**: A string indicating the status information (default is "OK").
    """

    status: str = "OK"
