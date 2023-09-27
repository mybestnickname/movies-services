from pydantic import BaseModel

from datetime import datetime


class Score(BaseModel):
    user_id: str
    movie_id: str
    score: float
    time_stamp: datetime
