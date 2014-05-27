import autocomplete_light
from .models import StudentWorker
from ecwsp.sis.autocomplete_light_registry import UserAutocomplete

autocomplete_light.register(StudentWorker, UserAutocomplete)
