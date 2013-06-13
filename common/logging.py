import sys, traceback

class SuppressUnreadablePost(object):
    def filter(self, record):
        _, exception, tb = sys.exc_info()
        if isinstance(exception, IOError):
            for _, _, function, _ in traceback.extract_tb(tb):
                if function == '_get_raw_post_data':
                    return False
        return True
