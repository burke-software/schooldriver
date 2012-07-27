from __future__ import absolute_import

from ecwsp.celery import celery

@celery.task(name='ecwsp.tasks.add')
def add(x, y):
    return x + y