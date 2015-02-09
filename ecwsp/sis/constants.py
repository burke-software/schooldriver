from django.db import models


class WeightField(models.DecimalField):
    def __init__(self, separator=",", *args, **kwargs):
        kwargs['max_digits'] = 5
        kwargs['decimal_places'] = 4
        kwargs['default'] = 1
        super(WeightField, self).__init__(*args, **kwargs)


class GradeField(models.DecimalField):
    def __init__(self, separator=",", *args, **kwargs):
        kwargs['max_digits'] = 8
        kwargs['decimal_places'] = 2
        kwargs['blank'] = True
        kwargs['null'] = True
        super(GradeField, self).__init__(*args, **kwargs)
