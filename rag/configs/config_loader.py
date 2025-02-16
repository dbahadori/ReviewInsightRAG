import os

import yaml
from pathlib import Path

from rag.configs.settings import Settings


class AttrDict(dict):
    """A dictionary that allows attribute-style access."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'AttrDict' has no attribute '{key}'")


def recursive_attr_dict(d):
    """Recursively converts dictionaries and lists to AttrDict."""
    if isinstance(d, dict):
        return AttrDict({k: recursive_attr_dict(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [recursive_attr_dict(i) for i in d]
    else:
        return d


class ConfigLoader:
    """
    Loads and validates a YAML configuration file.

    Provides:
      - The validated Pydantic model (get_validated_model)
      - The container-friendly model (get_container_config)
    """

    def __init__(
        self,
        config_path: str = os.path.join(
            os.path.dirname(__file__),
            'rag_config.yaml'
        )
    ):
        self.config_path = config_path
        self._validated_model = None  # Instance of Settings
        self._container_config = None  # Recursive AttrDict

    def load(self):
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(config_file, "r", encoding="utf-8") as file:
            raw_config = yaml.safe_load(file) or {}

        # Validate using the Pydantic Settings model
        self._validated_model = Settings(**raw_config)
        # Use model_dump (for Pydantic V2) to get a dict
        validated_dict = self._validated_model.model_dump()
        # Convert the dict to a recursive AttrDict for container use
        self._container_config = recursive_attr_dict(validated_dict)

    def get_validated_model(self) -> Settings:
        """Returns the validated Pydantic model (typed configuration)."""
        if self._validated_model is None:
            self.load()
        return self._validated_model

    def get_container_config(self) -> AttrDict:
        """Returns the container-friendly configuration (supports attribute access and .get())."""
        if self._container_config is None:
            self.load()
        return self._container_config
