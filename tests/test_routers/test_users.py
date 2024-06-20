from uuid import uuid4
import pytest
from fastapi import status

from ums import models, schemas
from ums.config import settings
from httpx import AsyncClient

base_endpoint = "/api/users"


@pytest.mark.anyio
class TestUserRetrievalEndpoints:
    """Tests for the user retrieval endpoints."""

    async def test_retrieve_users_when_none_is_created(
        self, api_client: AsyncClient
    ):
        """Test the retrieval of all users when no users have been created."""
        response = await api_client.get(base_endpoint)

        assert response.status_code == status.HTTP_200_OK
        result = schemas.UserResponse(**response.json())

        # ensure all the schema fields are present
        assert "message" in result.model_dump()
        assert "status_code" in result.model_dump()
        assert "data" in result.model_dump()

        # now let's check for the values
        assert result.message == "User data retrieval successful"
        assert result.status_code == 200
        assert isinstance(result.data, list)
        assert len(result.data) == 0

    async def test_retrieve_user_by_username(
        self, api_client: AsyncClient, create_jdoe_user
    ):
        """Test the retrieval of a user by their username."""
        user = create_jdoe_user
        assert user is not None
        assert isinstance(user, models.User)
        assert user.username == "jdoe"

        response = await api_client.get(
            base_endpoint, params={"username": user.username}
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json().get("data")
        # verify that the data field is a dictionary when retrieving a
        # single user.
        assert isinstance(data, dict)

        # verify that the user object serializes well with the schema
        user_data = schemas.User(**data)
        assert user_data.username == user.username

    async def test_retrieve_user_by_id(
        self, api_client: AsyncClient, create_jdoe_user
    ):
        """Test the retrieval of a user by their ID."""
        user = create_jdoe_user
        assert isinstance(user, models.User)
        assert user.id is not None

        response = await api_client.get(f"{base_endpoint}/{user.id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json().get("data")
        # Verify that the data field is a dictionary when retrieving a single
        # user.
        assert isinstance(data, dict)

        # Verify that the user object serializes well with the schema
        user_data = schemas.User(**data)
        assert user_data.id == user.id

    # create 5 dummy users with the API and then retrieve them
    async def test_retrieve_all_users(self, api_client: AsyncClient):
        """Test the retrieval of all users."""
        for i in range(5):
            response = await api_client.post(
                base_endpoint,
                json={"username": f"user_{i}", "password": f"password_{i}"},
            )
            assert response.status_code == status.HTTP_201_CREATED

        response = await api_client.get(base_endpoint)
        assert response.status_code == status.HTTP_200_OK

        data = response.json().get("data")
        assert isinstance(data, list)
        assert len(data) == 5

        for i, user_data in enumerate(data):
            user = schemas.User(**user_data)
            assert user.username == f"user_{i}"

    # test the retrieval of a user that does not exist
    async def test_retrieve_non_existent_user(self, api_client: AsyncClient):
        """Test the retrieval of a user that does not exist."""
        # first let's test when it's an ID passed as a path parameter
        response = await api_client.get(f"{base_endpoint}/{str(uuid4())}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # now let's test when it's a username passed as a query parameter
        response = await api_client.get(
            f"{base_endpoint}?username=non_existent"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # test the retrieval of a user with an invalid ID
    async def test_retrieve_user_with_invalid_id(
        self, api_client: AsyncClient
    ):
        """Test the retrieval of a user with an invalid ID."""
        response = await api_client.get(f"{base_endpoint}/invalid_id")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
class TestUserCreationEndpoint:
    """Tests for the user creation endpoint."""

    async def test_create_a_single_user(self, api_client: AsyncClient):
        """Test the creation of a single user."""
        response = await api_client.post(
            base_endpoint,
            json={"username": "jdoe", "password": "password1234"},
        )

        # explicitly ensure the response matches the schema
        schemas.UserResponse(**response.json())
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize(
        "username, password, expected_status_code",
        [
            ("jdoe", "password1", status.HTTP_201_CREATED),
            ("jane", "password2", status.HTTP_201_CREATED),
            ("bob", "bob_pass", status.HTTP_201_CREATED),
            ("pearl", "p3e-ert!", status.HTTP_201_CREATED),
            ("june_", "june_is_june", status.HTTP_201_CREATED),
        ],
    )
    async def test_create_multiple_valid_users(
        self,
        api_client: AsyncClient,
        username,
        password,
        expected_status_code,
    ):
        """Test the creation of multiple users with valid data."""
        response = await api_client.post(
            base_endpoint, json={"username": username, "password": password}
        )

        assert response.status_code == expected_status_code

    async def test_short_password(self, api_client: AsyncClient):
        """
        Test user creation with number of characters not meeting requirement.
        """
        response = await api_client.post(
            base_endpoint, json={"username": "jdoe", "password": "short"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        detail = response.json().get("detail")

        min_length = detail[0].get("ctx").get("min_length")
        assert min_length == settings.minimum_password_length

    async def test_create_existing_user(self, api_client: AsyncClient):
        """Test the creation of a user that already exists"""
        user_data = {"username": "bob_man", "password": "p455w0rd$%"}

        response = await api_client.post(base_endpoint, json=user_data)
        assert response.status_code == status.HTTP_201_CREATED

        # now let's create the same user once more
        response = await api_client.post(base_endpoint, json=user_data)
        assert response.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.parametrize(
        "username, password, expected",
        [
            # Happy path tests
            ("testuser", "password123", status.HTTP_201_CREATED),
            ("user", "securepassword", status.HTTP_201_CREATED),
            (
                "another.user",
                "anotherpassword",
                status.HTTP_201_CREATED,
            ),
            # Edge cases
            (
                "",
                "password123",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),  # Empty username
            (
                "testuser5",
                "",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),  # Empty password
            (
                "abc",
                "short",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),  # Password too short
            (
                "longusername",
                "longpassword",
                status.HTTP_201_CREATED,
            ),  # Long username and password
            # Error cases
            (
                "ab",
                "password123",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),  # Invalid username
            (
                "kent",
                "short",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),  # Password too short
            (
                "bruce",
                None,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),  # None password
            (
                None,
                "password123",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),  # None username
        ],
        ids=[
            "valid_username_password_1",
            "valid_username_password_2",
            "valid_username_password_3",
            "empty_username",
            "empty_password",
            "minimal_valid_username_short_password",
            "long_username_long_password",
            "invalid_username_format",
            "short_password",
            "none_password",
            "none_username",
        ],
    )
    async def test_create_multiple_users(
        self,
        api_client: AsyncClient,
        username: str,
        password: str,
        expected,
    ):
        """Test creating multiple users with valid and invalid data"""
        response = await api_client.post(
            base_endpoint, json={"username": username, "password": password}
        )

        assert response.status_code == expected


@pytest.mark.anyio
class TestUserUpdateEndpoint:
    """Tests for the user update endpoint."""

    async def test_update_user_by_id(
        self, api_client: AsyncClient, create_jdoe_user
    ):
        """Test the update of a user by their ID."""
        user = create_jdoe_user
        assert user is not None

        response = await api_client.put(
            f"{base_endpoint}/{user.id}",
            json={"username": "jdoe_updated", "password": "new_password"},
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json().get("data")
        assert data is not None

        user_data = schemas.User(**data)
        assert user_data.username == "jdoe_updated"

    async def test_update_non_existent_user(self, api_client: AsyncClient):
        """Test updating a user that does not exist."""
        response = await api_client.put(
            f"{base_endpoint}/{str(uuid4())}",
            json={"username": "jdoe_updated", "password": "new_password"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_user_with_invalid_id(self, api_client: AsyncClient):
        """Test updating a user with an invalid ID."""
        response = await api_client.put(
            f"{base_endpoint}/invalid_id",
            json={"username": "jdoe_updated", "password": "new_password"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_user_with_short_password(
        self, api_client: AsyncClient, create_jdoe_user
    ):
        """Test updating a user with a short password."""
        user = create_jdoe_user
        assert user is not None

        response = await api_client.put(
            f"{base_endpoint}/{user.id}",
            json={"username": "jdoe_updated", "password": "short"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        detail = response.json().get("detail")
        min_length = detail[0].get("ctx").get("min_length")
        assert min_length == settings.minimum_password_length

    # do the same tests but with the username as the identifier
    async def test_update_user_by_username(
        self, api_client: AsyncClient, create_jdoe_user
    ):
        """Test updating a user by their username."""
        user = create_jdoe_user
        assert user is not None

        old_username = user.username
        response = await api_client.put(
            f"{base_endpoint}?username={user.username}",
            json={"username": "jdoe_updated", "password": "new_password"},
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json().get("data")
        assert data is not None

        user_data = schemas.User(**data)
        assert user_data.username == "jdoe_updated"

        # now that the username has been updated, let's try to retrieve the
        # user by the old username and confirm that they do not exist
        response = await api_client.get(
            f"{base_endpoint}?username={old_username}"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_non_existent_user_by_username(
        self, api_client: AsyncClient
    ):
        """Test updating a user that does not exist by their username."""
        response = await api_client.put(
            f"{base_endpoint}?username=non_existent",
            json={"username": "jdoe_updated", "password": "new_password"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
class TestUserDeletionEndpoint:
    """Tests for the user deletion endpoint."""

    async def test_delete_user_by_id(
        self, api_client: AsyncClient, create_jdoe_user
    ):
        """Test the deletion of a user by their ID."""
        user = create_jdoe_user
        assert user is not None

        response = await api_client.delete(f"{base_endpoint}/{user.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # as a final check, let's try to retrieve the user and confirm that
        # they do not exist
        response = await api_client.get(f"{base_endpoint}/{user.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_user_by_username(
        self, api_client: AsyncClient, create_jdoe_user
    ):
        """Test the deletion of a user by their username."""
        user = create_jdoe_user
        assert user is not None

        response = await api_client.delete(
            f"{base_endpoint}?username={user.username}"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # as a final check, let's try to retrieve the user and confirm that
        # they do not exist
        response = await api_client.get(
            f"{base_endpoint}?username={user.username}"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_non_existent_user(
        self, api_client: AsyncClient, create_jdoe_user
    ):
        """Test the deletion of a user that does not exist."""
        user = create_jdoe_user
        assert user is not None

        response = await api_client.delete(f"{base_endpoint}/{str(uuid4())}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_user_with_invalid_id(self, api_client: AsyncClient):
        """Test the deletion of a user with an invalid ID."""
        response = await api_client.delete(f"{base_endpoint}/invalid_id")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
