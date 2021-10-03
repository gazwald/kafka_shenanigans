#!/usr/bin/env python3
import os
import avro.schema
import avro.io

from fixtures import price_example_1, price_example_2


def main():
    schema_dir = "./schemas"
    for schema in os.listdir(schema_dir):
        path = os.path.join(schema_dir, schema)
        with open(path, "r") as f:
            s = avro.schema.parse(f.read())
            print(avro.io.validate(s, price_example_1))
            print(avro.io.validate(s, price_example_2))


if __name__ == "__main__":
    main()
