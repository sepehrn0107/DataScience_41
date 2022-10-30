import yaml
import json

log_tag = "[Config]"

def assert_type(tag: str, value, want: type) -> bool:
    assert value is not None, f"Required config field '{tag}' is missing."
    assert isinstance(value, want), f"Field '{tag}' must be type '{want}'. Got '{type(value)}'."

class Config:
    def __init__(self, path="../config.yaml"):
        print(f"{log_tag}: Loading config.")

        with open("../config.yaml", mode="rt", encoding="utf-8") as file:
            cfg = yaml.safe_load(file)

            self.verbose = cfg.get("verbose", False)
            assert_type("verbose", self.verbose, bool)

            self.city = cfg.get("city")
            assert_type("city", self.city, str)

        if self.verbose:
            print(f"{log_tag}: Config loaded from '{path}'.")
            print(f"{log_tag}: {self}")

    def __str__(self):
        return json.dumps(self.__dict__, indent=2)