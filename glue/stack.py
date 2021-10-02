#!/usr/bin/env python3
import os
import avro.schema

import aws_cdk.aws_glue as glue
from aws_cdk import core as cdk


class GlueStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        registry = self.create_registry()
        schemas = list()
        schema_dir = "./schemas"
        for schema in os.listdir(schema_dir):
            path = os.path.join(schema_dir, schema)
            with open(path, 'r') as f:
                schema = avro.schema.parse(f.read())

            schemas.append(
                self.create_schema(
                    registry,
                    schema
                )
            )

    def create_schema(
        self,
        registry,
        schema,
        data_format: str = "AVRO",
        compatibility: str = "FORWARD",
    ):
        return glue.CfnSchema(
            self,
            schema.name + "schema",
            compatibility=compatibility,
            data_format=data_format,
            name=schema.name,
            schema_definition=str(schema),
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
