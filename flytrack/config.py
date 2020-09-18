import yaml

class Config:
    Instance = None

    @staticmethod
    def Load(pth):
        with open(pth) as fp:
            Config.Instance = Config(yaml.safe_load(fp))
        return Config.Instance

    def __init__(self, data):
        for (key, val) in data.items():
            if isinstance(val, dict):
                val = Config(val)

            setattr(self, key, val)
