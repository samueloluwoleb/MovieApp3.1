from abc import ABC, abstractmethod


class DataManagerInterface(ABC):
    """
        An interface that serves as a blueprint for other classes to be created.
        This interface manages the common data operations among different data sources
    """

    @abstractmethod
    def get_all_users(self):
        """
            Abstract method to be implemented by all inherited classes, used to return a List of all users
        :return:
        """
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """
            Abstract method to be implemented by all inherited classes, takes user id as parameter and
            returns a List of the user's favorite movies
        :param user_id:
        :return:
        """
        pass
