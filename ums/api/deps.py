from fastapi import Path, Query
from typing import Annotated
from fastapi import Depends
from ums.database import get_db
from sqlalchemy.orm import Session


DBSessionDependency = Annotated[Session, Depends(get_db)]

UsernameDependency = Query(..., description="The username of the user")
UserIdDependency = Path(..., description="The ID of the user")
