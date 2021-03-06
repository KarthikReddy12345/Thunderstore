from celery import shared_task

from thunderstore.repository.api.experimental.tasks import (
    update_api_experimental_caches,
)
from thunderstore.repository.api.v1.tasks import update_api_v1_caches


@shared_task
def update_api_caches():
    update_api_v1_caches()
    update_api_experimental_caches()
