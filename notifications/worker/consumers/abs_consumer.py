from abc import ABC, abstractmethod


class ABCConsumer(ABC):

    @abstractmethod
    def process_message(self):
        pass

    def _send_to_user(self):
        pass
