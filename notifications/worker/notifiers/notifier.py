from abc import ABC, abstractmethod


class AbstractNotifier(ABC):

    @abstractmethod
    def send_mass_email(self, **kwargs):
        """absmethod."""
        pass

    @abstractmethod
    def send_personal_email(self, **kwargs):
        """absmethod."""
        pass


