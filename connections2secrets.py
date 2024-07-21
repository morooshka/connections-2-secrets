#!/usr/bin/env python3

import argparse
import base64
import json
import logging
import os
import sys
from typing import Any, Dict, List

import jinja2
import yaml

ROOT: str = os.path.dirname(os.path.realpath(__file__))
FILE_NAME: str = os.path.basename(__file__)

PROCESSING_MAP: List[Dict[str, Any]] = [
    {"template": f"{ROOT}/templates/values.j2", "file": f"{ROOT}/values.yaml"},
    {"template": f"{ROOT}/templates/connections.j2", "file": f"{ROOT}/secret.yaml"}
]

logging.basicConfig(
    stream=sys.stdout,
    format="%(message)s",
    datefmt="%Y-%m-%d.%H:%M:%S"
)

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def generate_metadata(namespace: str, source_file_name: str) -> Dict[str, Any]:
    """Generate connections metadata."""
    metadata: Dict[str, Any] = {"namespace": namespace, "connections": []}

    try:
        with open(source_file_name, "r") as f:
            source: Dict[str, Any] = yaml.safe_load(f)
    except FileNotFoundError as e:
        logger.error(f"File not found: {source_file_name}")
        raise e

    for key, value in source.items():
        name: str = key
        data: str = base64.b64encode(bytes(json.dumps(value), "utf-8")).decode("utf-8")
        env_name: str = f"AIRFLOW_CONN_{key.upper()}"
        metadata["connections"].append({"name": name, "data": data, "env_name": env_name})

    return metadata


def render(environment: jinja2.Environment, metadata: Dict[str, Any]) -> List[str]:
    """Render templates."""
    generated: List[str] = []

    for item in PROCESSING_MAP:
        try:
            with open(item["template"], "r") as f:
                template = f.read()
        except FileNotFoundError as e:
            logger.error(f'File not found: {item["template"]}')
            raise e

        rendered: str = environment.from_string(template).render(**metadata)

        with open(item["file"], "w") as f:
            f.write(rendered)

        generated.append(os.path.basename(item["file"]))

    return generated


def main() -> None:
    """Main function"""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(FILE_NAME)
    parser.add_argument("--namespace", help="K8s namespace to create secrets", type=str, required=True)
    parser.add_argument("--source", help="An exported Airflow connections yaml file", type=str, required=True)
    args: argparse.Namespace = parser.parse_args()

    environment: jinja2.Environment = jinja2.Environment(loader=jinja2.BaseLoader())
    metadata: Dict[str, Any] = generate_metadata(namespace=args.namespace, source_file_name=args.source)
    generated: List[str] = render(environment=environment, metadata=metadata)
    logger.info(f'Connections successfully converted to {", ".join(generated)}')
    return


if __name__ == "__main__":
    main()
