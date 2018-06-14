from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class ApiConfig(AppConfig):
    name = 'project.api'

    def ready(self):
        logger.info('ready')
        from . import signals
