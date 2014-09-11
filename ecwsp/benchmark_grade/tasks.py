from django_sis.celery import app
from models import AggregateTask
from django.db import IntegrityError
from django_sis.celery import app
import logging

@app.task
def benchmark_aggregate_task(functions_and_arguments): #, affected_aggregates=()):
    # flag aggregates that are being recalculated
    #for aggregate in affected_aggregates:
    #    aggregate_task = AggregateTask(aggregate=aggregate, task_id=benchmark_aggregate_task.request.id)
    #    try:
    #        aggregate_task.save()
    #    except IntegrityError as e:
    #        logging.warning('We are calculating {} ({}) multiple times!'.format(aggregate, aggregate.pk), exc_info=True)

    # do the work
    for triplet in functions_and_arguments:
        function = triplet[0] # can't do much without this!
        try: args = triplet[1]
        except IndexError: args = () # okay, use empty tuple
        try: kwargs = triplet[2]
        except IndexError: kwargs = {} # okay, use empty dict
        #print 'celery calling {}({}, {})'.format(function, args, kwargs)
        function(*args, **kwargs)
    # remove flags
    goodbye = AggregateTask.objects.filter(task_id=benchmark_aggregate_task.request.id)
    aggregate_count = goodbye.count()
    goodbye.delete()
    # the return value appears in the log, so write something legible
    return "{} functions; {} Aggregates".format(len(functions_and_arguments), aggregate_count)
