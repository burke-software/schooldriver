# ------------------------------------------------------------------------------
def parseStyleAttribute(value, asDict=False):
    '''Returns a list of CSS (name, value) pairs (or a dict if p_asDict is
       True), parsed from p_value, which holds the content of a HTML "style"
       tag.'''
    if asDict: res = {}
    else:      res = []
    for attr in value.split(';'):
        if not attr.strip(): continue
        name, value = attr.split(':')
        if asDict: res[name.strip()] = value.strip()
        else:      res.append( (name.strip(), value.strip()) )
    return res
# ------------------------------------------------------------------------------
