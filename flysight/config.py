import yaml

class Config:
    """
    :class: Config

    Singleton class for parsing the configuration.
    """
    Instance = None

    @staticmethod
    def Load(pth: str):
        """
        Initial load of the configuration
        """
        assert Config.Instance is None, 'Config loaded twice'

        with open(pth) as fp:
            Config.Instance = Config(yaml.safe_load(fp))
        return Config.Instance

    def __init__(self, data: dict):
        """
        Create a dict->obj style object from the dict..
        """
        for (key, val) in data.items():
            if isinstance(val, dict):
                val = Config(val)

            setattr(self, key, val)
