from abc import ABC, abstractmethod


class ABSStorage(ABC):

    @abstractmethod
    def get_data(self, **kwargs):
        pass

    @abstractmethod
    def set_data(self, **kwargs):
        pass
