def cas_response_callbacks(tree):
    from django.conf import settings
    callbacks = []
    callbacks.extend(settings.CAS_RESPONSE_CALLBACKS)
    for path in callbacks:
        i = path.rfind('.')
        module, callback = path[:i], path[i+1:]
        try:
            mod = __import__(module, fromlist=[''])
        except ImportError as e:
            print "Import Error: %s" % e
        try:
            func = getattr(mod, callback)
        except AttributeError, e:
            print "Attribute Error: %s" % e
        func(tree)