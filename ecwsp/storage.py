'''
I seriously disagree with the developer's position given at:
https://code.djangoproject.com/ticket/18958#comment:4
A CSS error in some random third-party package should NOT
break my *entire* project and not allow me to run
collectstatic! Why not just fall back gracefully to
cache-less behavior? --jnm
'''

from django.contrib.staticfiles.storage import CachedStaticFilesStorage
import logging
class LessObnoxiousCachedStaticFilesStorage(CachedStaticFilesStorage):
    def hashed_name(self, name, content=None):
        try:
            return super(LessObnoxiousCachedStaticFilesStorage, self).hashed_name(name, content)
        except ValueError as e:
            logging.warning(e.message, exc_info=True)
            return name
