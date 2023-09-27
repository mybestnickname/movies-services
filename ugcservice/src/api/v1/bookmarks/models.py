from typing import List, Optional

from pydantic import BaseModel
from services.bookmarks.models import FilmBookmark


class NewFilmBookmarkRespBody(FilmBookmark):
    mongo_object_id: Optional[str]


class ListFilmBookmarkResponseModel(BaseModel):
    records: List[FilmBookmark]
    current_page: int
    page_size: int
    total_docs_count: int
    total_page_count: int


class DeleteBookmarkResponseModel(BaseModel):
    message: str = "Bookmark has been deleted."
