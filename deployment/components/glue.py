from typing import Dict

import avro.schema
from aws_cdk import aws_glue as glue
from constructs import Construct

__all__ = ["SchemaRegistryContruct", "SchemaConstruct", "SchemaVersionConstruct"]


class SchemaRegistryContruct(Construct):
    def __init__(self, scope: Construct, id, *, parameters: Dict):
        super().__init__(
            scope,
            id,
        )

        registry = self.create_registry()

    def create_registry(self):
        return glue.CfnRegistry(self, "registry", name="oanda")


class SchemaConstruct(Construct):
    def __init__(self, scope: Construct, id, *, parameters: Dict):
        super().__init__(
            scope,
            id,
        )

        self.schema = self.create_schema(**parameters)

    def create_schema(
        self,
        registry,
        schema,
        data_format: str = "AVRO",
        compatibility: str = "NONE",
    ):
        return glue.CfnSchema(
            self,
            schema.name,
            name=schema.name,
            compatibility=compatibility,
            data_format=data_format,
            schema_definition=str(schema),
            registry=registry,
        )


class SchemaVersionConstruct(Construct):
    def __init__(self, scope: Construct, id, *, parameters: Dict):
        super().__init__(
            scope,
            id,
        )

        self.schema_version = self.create_schema_version(**parameters)

    def create_schema_version(self, schema, registry, version):
        schema_prop = glue.CfnSchemaVersion.SchemaProperty(
            registry_name=registry.name, schema_name=schema.name
        )
        return glue.CfnSchemaVersion(
            self, version, schema=schema_prop, schema_definition=str(schema)
        )
