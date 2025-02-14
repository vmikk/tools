#!/usr/bin/env python

import glob
import logging
import os

import jsonschema
import requests
import yaml


def actions_schema_validation(self):
    """Checks that the GitHub Action workflow yml/yaml files adhere to the correct schema

    nf-core pipelines use GitHub actions workflows to run CI tests, check formatting and also linting, among others.
    These workflows are defined by ``yml`` scripts in ``.github/workflows/``. This lint test verifies that these scripts are valid
    by comparing them against the `JSON schema for GitHub workflows <https://json.schemastore.org/github-workflow>`_.

    To pass this test, make sure that all your workflows contain the required properties ``on`` and ``jobs`` and that
    all other properties are of the correct type, as specified in the schema (link above).
    """
    passed = []
    failed = []

    # Only show error messages from schema
    logging.getLogger("nf_core.schema").setLevel(logging.ERROR)

    # Get all workflow files
    action_workflows = glob.glob(os.path.join(self.wf_path, ".github/workflows/*.y*ml"))

    # Load the GitHub workflow schema
    r = requests.get("https://json.schemastore.org/github-workflow", allow_redirects=True)
    schema = r.json()

    # Validate all workflows against the schema
    for wf_path in action_workflows:
        wf = os.path.basename(wf_path)

        # load workflow
        try:
            with open(wf_path, "r") as fh:
                wf_json = yaml.safe_load(fh)
        except Exception as e:
            failed.append(f"Could not parse yaml file: {wf}, {e}")
            continue

        # yaml parses 'on' as True --> try to fix it before schema validation
        try:
            wf_json["on"] = wf_json.pop(True)
        except Exception:
            failed.append("Missing 'on' keyword in {}.format(wf)")

        # Validate the workflow
        try:
            jsonschema.validate(wf_json, schema)
            passed.append(f"Workflow validation passed: {wf}")
        except Exception as e:
            failed.append(f"Workflow validation failed for {wf}: {e}")

    return {"passed": passed, "failed": failed}
