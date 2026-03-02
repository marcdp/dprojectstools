from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json

# consts
DEFAULT_SCHEMA_VERSION = 1

# SecretValue
@dataclass
class SecretValue:
    """
    Holds the encrypted value string.
    Expected format: enc:v1:<backend>:<blob>
    """
    content: str

    def is_encrypted(self) -> bool:
        return self.content.startswith("enc:")

    def __str__(self) -> str:
        return self.content

# SecretEntry
@dataclass
class SecretEntry:
    """
    Represents a single secret entry.
    """
    key: str
    type: str
    services: List[str]
    value: SecretValue
    description: Optional[str] = None
    public: Optional[Dict[str, Any]] = None

    # Validation
    def validate(self) -> None:
        if not self.type:
            raise ValueError(f"Secret '{self.key}' missing type")

        if not self.services:
            raise ValueError(f"Secret '{self.key}' must define services")

        if not isinstance(self.value, SecretValue):
            raise ValueError(f"Secret '{self.key}' value must be SecretValue")

        if not self.value.is_encrypted():
            raise ValueError(f"Secret '{self.key}' value must be encrypted")

    # Serialization
    def to_dict(self) -> Dict[str, Any]:
        data = {
            "type": self.type,
            "services": self.services,
            "value": self.value.content,
        }

        if self.description:
            data["description"] = self.description

        if self.public is not None:
            data["public"] = self.public

        return data

    @staticmethod
    def from_dict(key: str, data: Dict[str, Any]) -> "SecretEntry":
        return SecretEntry(
            key=key,
            type=data["type"],
            services=data["services"],
            value=SecretValue(data["value"]),
            description=data.get("description"),
            public=data.get("public"),
        )


# SecretsMeta
@dataclass
class SecretsMeta:
    schema_version: int = DEFAULT_SCHEMA_VERSION
    extends: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = {"schema_version": self.schema_version}
        if self.extends:
            data["extends"] = self.extends
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SecretsMeta":
        return SecretsMeta(
            schema_version=data.get("schema_version", DEFAULT_SCHEMA_VERSION),
            extends=data.get("extends"),
        )


# SecretsStore
@dataclass
class SecretsStore:
    """
    Represents one environment file (e.g., dev.json).
    """
    name: str
    meta: SecretsMeta
    secrets: Dict[str, SecretEntry] = field(default_factory=dict)

    # Core Operations
    def add(self, entry: SecretEntry) -> None:
        if entry.key in self.secrets:
            raise ValueError(f"Secret '{entry.key}' already exists")
        self.secrets[entry.key] = entry

    def set(self, entry: SecretEntry) -> None:
        self.secrets[entry.key] = entry

    def remove(self, key: str) -> None:
        if key not in self.secrets:
            raise KeyError(f"Secret '{key}' not found")
        del self.secrets[key]

    def get(self, key: str) -> SecretEntry:
        if key not in self.secrets:
            raise KeyError(f"Secret '{key}' not found")
        return self.secrets[key]
    
    def exists(self, key: str) -> bool:
        return key in self.secrets

    def list_keys(self) -> List[str]:
        return sorted(self.secrets.keys())

    # Validation
    def validate(self) -> None:
        for entry in self.secrets.values():
            entry.validate()

    # Serialization
    def to_dict(self) -> Dict[str, Any]:
        return {
            "_meta": self.meta.to_dict(),
            "secrets": {
                key: entry.to_dict()
                for key, entry in sorted(self.secrets.items())
            },
        }

    def to_json(self, pretty: bool = True) -> str:
        if pretty:
            return json.dumps(self.to_dict(), indent=4)
        return json.dumps(self.to_dict(), separators=(",", ":"))

    @staticmethod
    def from_dict(name: str, data: Dict[str, Any]) -> "SecretsStore":
        meta = SecretsMeta.from_dict(data.get("_meta", {}))

        secrets_data = data.get("secrets", {})
        secrets = {
            key: SecretEntry.from_dict(key, value)
            for key, value in secrets_data.items()
        }

        return SecretsStore(
            name=name,
            meta=meta,
            secrets=secrets,
        )

    @staticmethod
    def from_json(name: str, raw: str) -> "SecretsStore":
        data = json.loads(raw)
        return SecretsStore.from_dict(name, data)