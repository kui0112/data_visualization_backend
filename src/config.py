import json
from typing import Dict


class Config:
    def __init__(self):
        self.static_objects_directory = "objects"
        self.log_level = "INFO"

    def parse(self, file: str):
        cfg: Dict = json.load(open(file))
        self.static_objects_directory = cfg.get("static_objects_directory")
        self.log_level = cfg.get("log_level")
        return self
