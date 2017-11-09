import json

class ConfigParser:
    def __init__(self) -> None:
        super().__init__()

    def parse(self, configFilePath = None):
        if configFilePath == None:
            return None
        else:
            self.configFilePath = configFilePath
            self.configFile = open(self.configFilePath)
            self.config = json.load(self.configFile)
            return self.config