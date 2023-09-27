from typing import List

from models.config import Base


class RecList(Base):
    movie_id: str
    rec_score: float


class NewRecReqModel(Base):
    user_id: str
    recommendations: List[RecList]

    class Config:
        schema_extra = {
            "example": {
                "user_id": "410fc89d-5b24-4170-a389-17f5fcb65d65",
                "recommendations": [
                    {
                        "movie_id": "11b75468-afb6-4721-bd4f-2eccffc546c2",
                        "rec_score": 4.87
                    },
                    {
                        "movie_id": "3f1dcb88-ebba-4b45-acb5-e6ddc723b632",
                        "rec_score": 4.75
                    },
                ]
            }

        }