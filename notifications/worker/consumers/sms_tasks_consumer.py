from consumers.abs_consumer import ABCConsumer


class SmsTasksConsumer(ABCConsumer):

    def __init__(self):
        raise NotImplementedError

    def process_message(self):
        raise NotImplementedError

    def _send_to_user(self):
        raise NotImplementedError
