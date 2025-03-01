from pydantic import BaseModel
from typing import List

class UserInfo(BaseModel):
    question: str
    choices: List[str] | None = None