from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    email: str
    description: str
    skills: Optional[list[str]] = None
