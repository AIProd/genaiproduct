import math
from dataclasses import asdict
from typing import Dict, Type, TypeVar, List, Tuple, Any, Optional

import numpy as np
import pandas as pd

from entities.account import Account
from entities.employee import Employee
from entities.hcp import HCP

T = TypeVar('T', bound=Account | HCP | Employee)


class EntityManager:

    def __init__(self):
        self.mappings: Dict[Type, Dict[str, str]] = {}
        self.foreign_keys: Dict[Type, Dict[str, Tuple[Type, str, str]]] = {}
        self.entities: Dict[Type, Dict[str, Any]] = {}

    def register_mapping(self, entity_class: Type[T], mapping: Dict[str, str]):
        """Register a mapping for an entity class."""
        self.mappings[entity_class] = mapping

    def get_mapping(self, entity_class: Type) -> Dict[str, str]:
        """Get the mapping for an entity class."""
        return self.mappings.get(entity_class, {})

    def register_foreign_key(self, entity_class: Type, fk_attr: str, related_class: Type, related_attr: str,
                             linking_attr: str):
        """
        Register a foreign key relationship between two entity classes.

        Parameters:
        - entity_class: The class of the entity that will have the foreign key attribute.
        - fk_attr: The name of the attribute in entity_class that will store the foreign key.
        - related_class: The class of the entity being referenced by the foreign key.
        - related_attr: The attribute in the related_class that is being referenced
                        (typically 'uuid' for the auto-generated identifier).
        - linking_attr: The name of the column in the original DataFrame that contains
                        the data to link entity_class instances to related_class instances.
        """
        if entity_class not in self.foreign_keys:
            self.foreign_keys[entity_class] = {}
        self.foreign_keys[entity_class][fk_attr] = (related_class, related_attr, linking_attr)

    def from_dataframe(self, df: pd.DataFrame, entity_class: Type[T], related_entities: Optional[List[T]] = None) -> \
    List[T]:
        """
        Create entity objects from a DataFrame using the registered mapping.
        This method also handles linking foreign keys if any are registered for the entity class.
        """
        mapping = self.mappings.get(entity_class, {})
        if not mapping:
            raise ValueError(f"No mapping registered for {entity_class.__name__}")

        missing_columns = set(mapping.values()) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Columns {missing_columns} not found in DataFrame")

        reverse_mapping = {v: k for k, v in mapping.items()}
        df_mapped = df.rename(columns=reverse_mapping)
        df_unique = df_mapped.drop_duplicates(mapping.keys())
        columns_to_replace = list(mapping.keys())
        df_unique[columns_to_replace] = df_unique[columns_to_replace].astype(object).where(df_unique[columns_to_replace].notna(), None)
        does_entity_class_have_foreign_key = entity_class in self.foreign_keys

        if does_entity_class_have_foreign_key:
            # Pre-process related entities for faster lookup
            related_entity_dict = {}
            for fk_attr, (related_class, related_attr, linking_attr) in self.foreign_keys[entity_class].items():
                related_entity_dict[fk_attr] = {
                    getattr(related_ent, related_attr): related_ent.uuid
                    for related_ent in related_entities
                }

        def create_entity(row):
            entity_data = row.to_dict()
            if all(entity_data.get(key) is None for key in mapping.keys()):
                return None

            entity = entity_class.from_dict(entity_data)

            if does_entity_class_have_foreign_key:
                for fk_attr, (_, _, linking_attr) in self.foreign_keys[entity_class].items():
                    linking_value = entity_data[linking_attr]
                    related_uuid = related_entity_dict[fk_attr].get(linking_value)
                    if related_uuid:
                        setattr(entity, fk_attr, related_uuid)

            return entity

        entities = df_unique.apply(create_entity, axis=1).tolist()
        original_generator = (item for item in entities if item is not None)

        filtered_list: List[T] = list(
            filter(lambda x: isinstance(x, (Account, HCP, Employee)), original_generator))

        return filtered_list

    @staticmethod
    def __validate_instance_types(instance_list, expected_type) -> bool:
        for index, item in enumerate(instance_list):
            if not isinstance(item, expected_type):
                return False

        return True

    @staticmethod
    def to_dataframe(entities: List[T]) -> pd.DataFrame:
        """Convert a list of entities to a DataFrame."""
        return pd.DataFrame([asdict(entity) for entity in entities])

    def supplement_entities(self, df: pd.DataFrame, entity_class: Type[T], entities: List[T]):
        """Replace original columns that corresponds to entity for unique uuid from entity"""
        mapping = self.mappings.get(entity_class, {})
        if not mapping:
            raise ValueError(f"No mapping registered for {entity_class.__name__}")

        missing_columns = set(mapping.values()) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Columns {missing_columns} not found in DataFrame")

        columns_to_replace = list(mapping.values())
        df[columns_to_replace] = df[columns_to_replace].astype(object).where(df[columns_to_replace].notna(), None)

        entity_key = f"{entity_class.__name__.lower()}_uuid"

        entity_dict = {tuple(getattr(entity, attr) for attr in mapping.keys()): str(entity.uuid) for entity in entities}

        def get_uuid(row):
            key = tuple(row[mapping[attr]] for attr in mapping.keys())
            return entity_dict.get(key, None)

        df[entity_key] = df.apply(get_uuid, axis=1)

        df_result = df.drop(columns=list(mapping.values()))

        return df_result




