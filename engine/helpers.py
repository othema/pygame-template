import json


class JSON:
    @staticmethod
    def load(path):
        with open(path) as f:
            return json.load(f)

    @staticmethod
    def write(data, path):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
