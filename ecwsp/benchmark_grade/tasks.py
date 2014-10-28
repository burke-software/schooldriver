from django.contrib.contenttypes.models import ContentType
from models import AggregateTask
from django_sis.celery import app
import logging

@app.task
def benchmark_calculation_task(content_type_id, object_id, *args, **kwargs):
    # We expect that flags are added synchronously by the calling function
    content_type = ContentType.objects.get_for_id(content_type_id)
    aggregate = content_type.get_object_for_this_type(pk=object_id)
    aggregate.calculate(*args, **kwargs)
    # remove flags
    goodbye = AggregateTask.objects.filter(
        task_id=benchmark_calculation_task.request.id,
        content_type=content_type,
        object_id=object_id
    )
    goodbye.delete()
    # the return value appears in the log, so write something legible
    return '{} #{}: {} {}'.format(
        type(aggregate).__name__,
        aggregate.pk,
        aggregate.cached_value,
        aggregate.cached_substitution
    )
