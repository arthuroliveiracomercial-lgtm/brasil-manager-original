from dataclasses import dataclass

import pandas as pd

from .data_loader import load_upload
from .database import Database
from .validation import Issue, validate_dataset, validate_relations


@dataclass
class ValidationResult:
    data: dict[str, pd.DataFrame]
    issues: list[Issue]

    @property
    def can_import(self) -> bool:
        return not any(item.severity == "erro" for item in self.issues)


def validate_upload(filename: str, content: bytes, database: Database, dataset: str | None = None) -> ValidationResult:
    raw = load_upload(filename, content, dataset)
    clean: dict[str, pd.DataFrame] = {}
    issues: list[Issue] = []
    for name, frame in raw.items():
        clean[name], local_issues = validate_dataset(name, frame)
        issues.extend(local_issues)
    issues.extend(validate_relations(clean, database.existing_ids()))
    return ValidationResult(clean, issues)

