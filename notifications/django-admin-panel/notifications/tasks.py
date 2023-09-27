import json
import os
import logging
from logging import config as logger_conf
from config.components.logging import LOGGING
from datetime import datetime
import requests
from celery import shared_task

from config.settings import NOTIFICATION_URL
from notifications.models import EmailNotificationTask

logger_conf.dictConfig(LOGGING)
logger = logging.getLogger()


def get_data_from_db(priority_levels: str):
    logger.info(f'Trying to get {priority_levels} tasks from DB.')
    notification_tasks = EmailNotificationTask.objects.filter(
        status__icontains=str(EmailNotificationTask.Status.CREATED)
    ).filter(
        scheduled_datetime__lte=datetime.now().isoformat(sep=" ")
    ).filter(
        priority_level__icontains=priority_levels
    )
    logger.info(f'Tasks {priority_levels} received.')
    return notification_tasks


def post_data_to_rabbit(task: EmailNotificationTask):
    try:
        logger.info(f'Trying send message to rabbit task {task.id}.')
        resp_res = requests.post(
            url=NOTIFICATION_URL,
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            json={
                'delivery_type': 'email',
                'template_name': str(task.name),
                'users_group': str(task.user_roles),
            },
        )
        if not resp_res.status_code == 200:
            logger.error(f'Error sending request to notification api {resp_res.text} task {task.id}')
        logger.info(f'Task {task.id} sent to rabbit')
        return resp_res
    except Exception as ex:
        logger.error(f'The request failed notification service {ex}')


def send_task_process(notification_tasks):
    result_message_list = []
    for task in notification_tasks:
        resp_res = post_data_to_rabbit(task)
        if resp_res.status_code:
            task.status = str(EmailNotificationTask.Status.IN_PROCESS)
            task.sending_datetime = datetime.now().isoformat(sep=" ")
            task.save()
            result_message_list.append(str(task.id))
    return json.dumps({'submitted_tasks': result_message_list})


@shared_task
def email_tasks_high_priority():
    notification_tasks = get_data_from_db(str(EmailNotificationTask.PriorityLevels.HIGH))
    if not notification_tasks:
        logger.info(f'There are no active tasks with high priority in the Database.')
        return 'There are no active tasks with high priority in the Database.'

    return send_task_process(notification_tasks)


@shared_task
def email_tasks_mid_priority():
    notification_tasks = get_data_from_db(str(EmailNotificationTask.PriorityLevels.MID))
    if not notification_tasks:
        logger.info(f'There are no active tasks with mid priority in the Database.')
        return 'There are no active tasks with mid priority in the Database.'
    return send_task_process(notification_tasks)


@shared_task
def email_tasks_low_priority():
    notification_tasks = get_data_from_db(str(EmailNotificationTask.PriorityLevels.LOW))
    if not notification_tasks:
        logger.info(f'There are no active tasks with low priority in the Database.')
        return 'There are no active tasks with low priority in the Database.'
    return send_task_process(notification_tasks)
