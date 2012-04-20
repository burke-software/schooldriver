from ajax_select import LookupChannel

from models import Day

class DayLookup(LookupChannel):
    model = Day
    search_field = 'day'
    def get_query(self,q,request):
        qs = []
        for day in Day.objects.all()[0].dayOfWeek:
            if q.lower() in day[1].lower():
                qs.append(Day.objects.get(day=day[0]))
        return qs