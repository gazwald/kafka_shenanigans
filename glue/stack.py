#!/usr/bin/env python3
import os

import avro.schema
import aws_cdk.aws_glue as glue
import boto3
from aws_cdk import core as cdk


class SchemaStack(cdk.NestedStack):
    def __init__(self, scope, id, *, parameters=None):
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


class SchemaVersionStack(cdk.NestedStack):
    def __init__(self, scope, id, *, parameters=None):
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


class GlueStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.glue = boto3.client("glue", region_name="ap-southeast-2")

        registry = self.create_registry()
        registry_property = glue.CfnSchema.RegistryProperty(name=registry.name)

        schema_dir = "./schemas"
        for schema in os.listdir(schema_dir):
            schema_path = os.path.join(schema_dir, schema)
            schema_construct = None

            for version in os.listdir(schema_path):
                version_path = os.path.join(schema_path, version)
                with open(version_path, "r") as f:
                    s = avro.schema.parse(f.read())
                    if "v1" in version_path:
                        schema_construct = SchemaStack(
                            self,
                            s.name,
                            parameters={"registry": registry_property, "schema": s},
                        )
                    else:
                        if schema_construct:
                            SchemaVersionStack(
                                self,
                                version,
                                parameters={
                                    "registry": registry_property,
                                    "schema": s,
                                    "version": version,
                                },
                            )

    def create_registry(self):
        return glue.CfnRegistry(self, "registry", name="oanda")


def main():
    app = cdk.App()

    GlueStack(
        app,
        "glue",
        env=cdk.Environment(
            account=os.getenv("CDK_DEFAULT_ACCOUNT"), region="ap-southeast-2"
        ),
    )

    app.synth()


if __name__ == "__main__":
    main()
