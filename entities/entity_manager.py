from typing import Dict, Type, Optional, Any, TypeVar
from uuid import uuid4

import polars as pl
from polars import Int64, Float64, String, Boolean

from entities.entity_classes.account import Account
from entities.entity_classes.employee import Employee
from entities.entity_classes.hcp import HCP

T = TypeVar('T', bound=Account | HCP | Employee)


class EntityManager:
    def __init__(self):
        self.entity_cache: Dict[Type[T], pl.LazyFrame] = {}
        self.mappings: Dict[Type[T], Dict[str, str]] = {}
        self.relations: Dict[Type[T], Dict[str, Dict[str, str]]] = {}

    def register_mapping(self, entity_class: Type[T], mapping: Optional[Dict[str, str]] = None):
        self.mappings[entity_class] = mapping
        schema = self.get_entity_schema(entity_class)
        self.entity_cache[entity_class] = pl.LazyFrame(schema=schema)

    def register_relation(
            self,
            entity_class: Type[T],
            related_class: Type[T],
            relation_attribute: str,
            related_attribute: str,
            linking_attribute: str,
            linking_column: str
    ):
        self.relations[entity_class] = {
            related_class: {
                'relation_attribute': relation_attribute,
                'related_attribute': related_attribute,
                'linking_attribute': linking_attribute,
                'linking_column': linking_column
            }
        }

    @staticmethod
    def get_entity_schema(entity_class: Type[T]) -> dict[Any, Type[Int64 | Float64 | String | Boolean]]:
        type_mapping = {
            int: pl.Int64,
            float: pl.Float64,
            str: pl.Utf8,
            bool: pl.Boolean,
        }

        return {
            attr: type_mapping.get(typ, pl.Utf8)
            for attr, typ in entity_class.__annotations__.items()
        }

    def from_lazy_frame(self, entity_class: Type[T], lazy_frame: pl.LazyFrame) -> pl.LazyFrame:
        mapping = self.mappings[entity_class]

        select_columns = list(mapping.values())
        rename_mapping = {v: k for k, v in mapping.items()}

        has_relation = False
        if self.relations.get(entity_class):
            has_relation = True
            for entity, relation_mapping in self.relations[entity_class].items():
                select_columns.append(relation_mapping['linking_column'])

        new_data_lf = lazy_frame.select(
            select_columns,
        ).rename(rename_mapping).unique()

        height = new_data_lf.select(pl.len()).collect().item()

        new_data_lf = new_data_lf.with_columns(
            pl.Series(name='uuid', values=[str(uuid4()) for _ in range(height)])
        )

        if has_relation:
            for entity, relation_mapping in self.relations[entity_class].items():
                cached_entity_lf = self.entity_cache[entity]
                new_data_lf = new_data_lf.join(
                    cached_entity_lf.select(
                        pl.col(relation_mapping['linking_attribute']),
                        pl.col(relation_mapping['related_attribute']).alias(relation_mapping['relation_attribute']),
                    ),
                    left_on=relation_mapping['linking_column'],
                    right_on=relation_mapping['linking_attribute'],
                    how='left'
                )

        self.entity_cache[entity_class] = new_data_lf.select(entity_class.__annotations__.keys())

        return self.entity_cache[entity_class]

    def get_by_primary_key(self, entity_class: Type[T], key: Any) -> Optional[T]:
        primary_key = entity_class.get_primary_key()
        if not primary_key:
            raise ValueError(f"No primary key defined for {entity_class.__name__}")

        result = (
            self.entity_cache[entity_class]
            .filter(pl.col(primary_key) == key)
            .collect()
        )

        if result.is_empty():
            return None

        row = result.row(0, named=True)
        return entity_class(**row)
