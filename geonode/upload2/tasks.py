from __future__ import absolute_import

from celery import shared_task
import time

@shared_task
def do_stuff(thingee):
    time.sleep(1)
    print 'doing stuff', thingee

