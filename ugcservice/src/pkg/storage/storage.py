from abc import ABC, abstractmethod


class ABSStorage(ABC):

    @abstractmethod
    def send_to_ugc_storage(self, **kwargs):
        """absmethod."""
        pass

    @abstractmethod
    def create_or_update_in_ugc_storage(self, **kwargs):
        """absmethod."""
        pass

    @abstractmethod
    def get_ugc_from_storage(self, **kwargs):
        """absmethod."""
        pass

    @abstractmethod
    def delete_ugc_from_storage(self, **kwargs):
        """absmethod."""
        pass

    @abstractmethod
    def get_ugc_count_in_storage(self, **kwargs):
        """absmethod."""
        pass

    @abstractmethod
    def get_ugc_data_chunks(self, **kwargs):
        """absmethod."""
        pass

    @abstractmethod
    def get_avg_ugc_data(self, **kwargs):
        """absmethod."""
        pass
