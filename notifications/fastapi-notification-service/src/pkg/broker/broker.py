from abc import ABC, abstractmethod


class AbstractBroker(ABC):

    @abstractmethod
    def get_from_broker(self, **kwargs):
        """absmethod."""
        pass

    @abstractmethod
    def send_to_broker(self, **kwargs):
        """absmethod."""
        pass
