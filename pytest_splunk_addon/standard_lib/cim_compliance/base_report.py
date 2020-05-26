import abc


@abc.ABC
class CIMReport(object):
    """
    Interface for CIM report.
    """

    @abc.abstractmethod
    def set_title(self, string):
        raise NotImplementedError()

    @abc.abstractmethod
    def add_section_title(self, string):
        raise NotImplementedError()

    @abc.abstractmethod
    def add_section_note(self, string):
        raise NotImplementedError()

    @abc.abstractmethod
    def add_table(self, string):
        raise NotImplementedError()

    @abc.abstractmethod
    def write(self, path):
        raise NotImplementedError()
