from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ums import schemas
from ums.api.routers import users
from ums.config import settings

if settings.dev:
    servers = {
        "url": "http://localhost:8000",
        "description": "Local development server",
    }
else:
    servers = {"url": settings.prod_url, "description": "Production server"}

description = """
This User Management System provides basic functionality to manage users
through REST APIs, allowing users to be retrieved by ID or all users to be
listed. Users can also be created, updated, and deleted.
"""


app = FastAPI(
    title="User Management System REST APIs",
    summary="A simple User Management System",
    description=description,
    docs_url="/api/",
    redoc_url="/api/docs",
    openapi_tags=[
        {"name": "Users", "description": "Operations related to users"},
        {
            "name": "API Status",
            "description": "An endpoint to check the status of the API",
        },
    ],
    contact={
        "name": "Maxwell Nana Forson",
        "url": "https://linktr.ee/theLazyProgrammer",
        "email": "nanaforsonjnr@gmail.com",
    },
    version="v1.0",
    servers=[servers],
)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api")


@router.get(
    "/status",
    tags=["API Status"],
    response_model=schemas.StatusResponse,
    response_description="API Status OK",
    summary="API status",
)
async def get_api_status():
    """Returns OK if the API is up and running"""
    return {"status": "OK"}


router.include_router(users.router)
app.include_router(router)
