from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    A class to manage settings for the user management system.

    Explanation:
    This class defines settings for the user management system, including
    database connection details, development mode flag, and password length
    requirements. The settings are loaded from environment variables or a .env

    Args:
    - **db_user**: The username for the database connection.
    - **db_name**: The name of the database.
    - **db_host**: The host of the database (default is "localhost").
    - **db_password**: The password for the database connection.
    - **db_port**: The port for the database connection.
    - **dev**: A flag indicating whether the system is in development mode
    (default is False).
    - **minimum_password_length**: The minimum required length for user
    passwords (default is 8).
    - **maximum_password_length**: The maximum allowed length for user
    passwords (default is 15).
    """

    db_user: str
    db_name: str
    db_host: str = "localhost"
    db_password: str
    db_port: int
    dev: bool = False
    minimum_password_length: int = 8
    maximum_password_length: int = 15

    model_config = ConfigDict(env_file=".env")


settings = Settings()
