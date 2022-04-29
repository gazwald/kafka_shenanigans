import os

import avro.schema
from aws_cdk import NestedStack
from aws_cdk import aws_glue as glue
from constructs import Construct

from components.glue import SchemaConstruct, SchemaVersionConstruct

__all__ = ["GlueStack"]


class GlueStack(NestedStack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        registry_property = glue.CfnSchema.RegistryProperty(name="oanda")

        schema_dir = "./schemas"
        for schema in os.listdir(schema_dir):
            schema_path = os.path.join(schema_dir, schema)
            schema_construct = None

            for version in os.listdir(schema_path):
                version_path = os.path.join(schema_path, version)
                with open(version_path, "r") as f:
                    s = avro.schema.parse(f.read())
                    if "v1" in version_path:
                        schema_construct = SchemaConstruct(
                            self,
                            s.name,
                            parameters={"registry": registry_property, "schema": s},
                        )
                    else:
                        if schema_construct:
                            SchemaVersionConstruct(
                                self,
                                version,
                                parameters={
                                    "registry": registry_property,
                                    "schema": s,
                                    "version": version,
                                },
                            )
