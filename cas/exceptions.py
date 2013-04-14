"CasTicketException, CasConfigException"
from django.core.exceptions import ValidationError

class CasTicketException(ValidationError):
    """The ticket fails to validate"""

class CasConfigException(ValidationError):
    """The config is wrong"""

