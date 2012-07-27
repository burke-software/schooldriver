from celery import task

@task(name='sum-of-two-numbers')
def add(x, y):
    return x + y