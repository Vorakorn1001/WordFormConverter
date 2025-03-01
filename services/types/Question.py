from pydantic import BaseModel
from typing import List

class Question(BaseModel):
    question: str
    choices: List[str]
    answer: str