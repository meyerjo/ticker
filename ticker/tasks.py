import logging
from datetime import timedelta

from celery import shared_task, task
from django.db import transaction
from django.utils.timezone import now

from ticker.models import FieldAllocation


@shared_task
@task(name='task.clean_up_fieldallocation')
def clean_up_fieldallocations():
    with transaction.atomic():
        field_allocations = FieldAllocation.objects.filter(is_active=True, create_time__lte=now()-timedelta(hours=16)).select_for_update()
        logger = logging.getLogger(__name__)
        logger.info('The following field-allocations are invalidated: ' + str(field_allocations))
        field_allocations.update(is_active=False)
