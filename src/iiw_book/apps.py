import os
import logging

from django.apps import AppConfig
from django.core.cache import cache

import requests

logger = logging.getLogger(__name__)

AGENT_URL = os.environ.get("AGENT_URL")


class IIWBookConfig(AppConfig):
    name = "iiw_book"

    def ready(self):
        # Runs at startup
        pass
