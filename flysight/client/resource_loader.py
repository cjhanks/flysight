from os import listdir
from os.path import basename, dirname, join, splitext


class Resource:
    """
    Static class singleton for loading CSS resources.  Integrating the QRC
    was a bit more work than I wanted to do.  So, I decided to write a simple
    CSS loader for stylizing the widgets.
    """
    __Data = None

    @staticmethod
    def Load() -> dict:
        """
        Initialize a dictionary with all of the resources.
        """
        data = {}
        root = join(dirname(__file__), 'resource')
        for pth in listdir(root):
            (name, _) = splitext(pth)
            with open(join(root, pth)) as fp:
                data[name] = fp.read()

        return data

    @staticmethod
    def Get(name: str) -> str:
        """
        Get the resource string.
        """
        if Resource.__Data is None:
            Resource.Data = Resource.Load()

        return Resource.Data[name]
