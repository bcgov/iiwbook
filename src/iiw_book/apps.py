import os
import logging

from django.apps import AppConfig
from django.core.cache import cache
from django.db.utils import ProgrammingError

import requests

logger = logging.getLogger(__name__)

AGENT_URL = os.environ.get("AGENT_URL")


class IIWBookConfig(AppConfig):
    name = "iiw_book"

    def ready(self):
        # Hack to let the manage command to create the cache table through...
        try:
            cache.get("")
        except ProgrammingError:
            return

        if cache.get("credential_definition_id") is None:
            schema_body = {
                "schema_name": "conference_attendance",
                "schema_version": "9000.0.20",
                "attributes": ["email", "full_name", "conference", "time"],
            }
            schema_response = requests.post(f"{AGENT_URL}/schemas", json=schema_body)

            logger.info(schema_response.text)

            schema_response_body = schema_response.json()
            schema_id = schema_response_body["schema_id"]

            credential_definition_body = {"schema_id": schema_id}
            credential_definition_response = requests.post(
                f"{AGENT_URL}/credential-definitions", json=credential_definition_body
            )

            logger.info(credential_definition_response.text)

            credential_definition_response_body = credential_definition_response.json()
            credential_definition_id = credential_definition_response_body[
                "credential_definition_id"
            ]

            logger.info(f"cred def id: {credential_definition_id}")

            cache.set("credential_definition_id", credential_definition_id, None)
