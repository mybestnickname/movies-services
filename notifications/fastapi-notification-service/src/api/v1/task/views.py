import http
import logging
from enum import Enum
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from services.task import TaskService, get_task_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/task',
    tags=["Add task to rabbit"]
)


class DeliveryType(str, Enum):
    sms = "sms"
    email = "email"


class RabbitTaskPostReqBody(BaseModel):
    delivery_type: DeliveryType = DeliveryType.email
    template_name: str = Field(
        description="To get template from template admin service.",
        default="welcome_email_template",
    )
    user_ids: Optional[List[UUID]] = Field(
        description="User ids to get mails from auth service.",
        default=[],
        example=["ddcb7980-7355-413a-84c2-f82d39e1ac03", "a42eba4d-9830-47b3-a90e-c04ed2490a0c"],
    )
    user_groups: Optional[str] = Field(
        description="User groups to get users from auth service.",
        default="",
        example="subscriber",
    )


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Task has been added to rabbit.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to add task to rabbit."},
                },
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Can't found queue in rabbit.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Can't found queue in rabbit.",
                    },
                },
            },
        },
    },
)
async def add_task_to_rabbit(
        params: RabbitTaskPostReqBody,
        task_service: TaskService = Depends(get_task_service)
) -> None:
    """Put notification to queue."""

    task = {
        'delivery_type': params.delivery_type,
        'template_name': params.template_name,
        'users_id': [str(i) for i in params.user_ids],
        'users_group': params.user_groups,
    }

    if not any((task['users_id'], task['users_group'])):
        raise HTTPException(status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY, detail="Set user_ids or user_groups.")

    await task_service.send_to_queue(params.delivery_type, task)
