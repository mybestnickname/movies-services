from fastapi import Query


from typing import List

from pydantic import BaseModel


class Paginator:
    def __init__(
            self,
            page_size: int = Query(
                default=20,
                gt=0,
                title="Page size",
                description="Number of posts per page.",
                alias="page[size]"),
            page_number: int = Query(
                default=1,
                gt=0,
                title="Page number",
                description="Pagination page number.",
                alias="page[number]"
            )
    ):
        self.page_size = page_size
        self.page_number = page_number


class PaginatedResponseModel(BaseModel):
    current_page: int
    page_size: int
    total_docs_count: int
    total_page_count: int
