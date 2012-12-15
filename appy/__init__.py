'''Appy allows you to create easily complete applications in Python.'''

# ------------------------------------------------------------------------------
import os.path

# ------------------------------------------------------------------------------
def getPath(): return os.path.dirname(__file__)
def versionIsGreaterThanOrEquals(version):
    '''This method returns True if the current Appy version is greater than or
       equals p_version. p_version must have a format like "0.5.0".'''
    import appy.version
    if appy.version.short == 'dev':
        # We suppose that a developer knows what he is doing, so we return True.
        return True
    else:
        paramVersion = [int(i) for i in version.split('.')]
        currentVersion = [int(i) for i in appy.version.short.split('.')]
        return currentVersion >= paramVersion

# ------------------------------------------------------------------------------
class Object:
    '''At every place we need an object, but without any requirement on its
       class (methods, attributes,...) we will use this minimalist class.'''
    def __init__(self, **fields):
        for k, v in fields.iteritems():
            setattr(self, k, v)
    def __repr__(self):
        res = u'<Object '
        for attrName, attrValue in self.__dict__.iteritems():
            v = attrValue
            if hasattr(v, '__repr__'):
                v = v.__repr__()
            try:
                res += u'%s=%s ' % (attrName, v)
            except UnicodeDecodeError:
                res += u'%s=<encoding problem> ' % attrName
        res  = res.strip() + '>'
        return res.encode('utf-8')
    def __nonzero__(self):
        return bool(self.__dict__)
# ------------------------------------------------------------------------------
