# ------------------------------------------------------------------------------
import types
from appy import Object
from appy.gen import Field
from appy.px import Px
from DateTime import DateTime
from BTrees.IOBTree import IOBTree
from persistent.list import PersistentList

# ------------------------------------------------------------------------------
class Calendar(Field):
    '''This field allows to produce an agenda (monthly view) and view/edit
       events on it.'''
    jsFiles = {'view': ('widgets/calendar.js',)}

    # Month view for a calendar. Called by pxView, and directly from the UI,
    # via Ajax, when the user selects another month.
    pxMonthView = Px('''
     <div var="field=zobj.getAppyType(req['fieldName']);
               ajaxHookId=zobj.UID() + field.name;
               month=req['month'];
               monthDayOne=DateTime('%s/01' % month);
               today=DateTime('00:00');
               grid=field.getMonthGrid(month);
               allEventTypes=field.getEventTypes(zobj);
               preComputed=field.getPreComputedInfo(zobj, monthDayOne, grid);
               defaultDate=field.getDefaultDate(zobj);
               defaultDateMonth=defaultDate.strftime('%Y/%m');
               previousMonth=field.getSiblingMonth(month, 'previous');
               nextMonth=field.getSiblingMonth(month, 'next');
               mayEdit=zobj.allows(widget['writePermission']);
               objUrl=zobj.absolute_url();
               startDate=field.getStartDate(zobj);
               endDate=field.getEndDate(zobj);
               otherCalendars=field.getOtherCalendars(zobj, preComputed)"
          id=":ajaxHookId">

      <script type="text/javascript">:'var %s_maxEventLength = %d;' % \
                                   (field.name, field.maxEventLength)"></script>

      <!-- Month chooser -->
      <div style="margin-bottom: 5px"
           var="fmt='%Y/%m/%d';
                goBack=not startDate or (startDate.strftime(fmt) &lt; \
                                         grid[0][0].strftime(fmt));
                goForward=not endDate or (endDate.strftime(fmt) &gt; \
                                          grid[-1][-1].strftime(fmt))">
       <!-- Go to the previous month -->
       <img class="clickable" if="goBack" src=":url('arrowLeftSimple')"
            onclick=":'askMonthView(%s,%s,%s,%s)' % \
                     (q(ajaxHookId),q(objUrl),q(field.name),q(previousMonth))"/>
       <!-- Go back to the default date -->
       <input type="button" if="goBack or goForward"
              var="fmt='%Y/%m';
                   label=(defaultDate.strftime(fmt)==today.strftime(fmt)) and \
                         'today' or 'goto_source'"
              value=":_(label)"
              onclick=":'askMonthView(%s, %s, %s, %s)' % (q(ajaxHookId), \
                                 q(objUrl), q(field.name), q(defaultDateMonth))"
              disabled=":defaultDate.strftime(fmt)==monthDayOne.strftime(fmt)"/>
       <!-- Go to the next month -->
       <img class="clickable" if="goForward" src=":url('arrowRightSimple')"
            onclick=":'askMonthView(%s, %s, %s, %s)' % (q(ajaxHookId), \
                                   q(objUrl), q(field.name), q(nextMonth))"/>
       <span>:_('month_%s' % monthDayOne.aMonth())</span>
       <span>:month.split('/')[0]</span>
      </div>

      <!-- Calendar month view -->
      <table cellpadding="0" cellspacing="0" width="100%" class="list"
             style="font-size: 95%"
             var="rowHeight=int(field.height/float(len(grid)))">
       <!-- 1st row: names of days -->
       <tr height="22px">
        <th for="dayName in field.getNamesOfDays(zobj)"
            width="14%">:dayName</th>
       </tr>
       <!-- The calendar in itself -->
       <tr for="row in grid" valign="top" height=":rowHeight">
        <x for="date in row"
           var2="tooEarly=startDate and (date &lt; startDate);
                 tooLate=endDate and not tooEarly and (date &gt; endDate);
                 inRange=not tooEarly and not tooLate;
                 cssClasses=field.getCellStyle(zobj, date, today)">
         <!-- Dump an empty cell if we are out of the supported date range -->
         <td if="not inRange" class=":cssClasses"></td>
         <!-- Dump a normal cell if we are in range -->
         <td if="inRange"
             var2="events=field.getEventsAt(zobj, date);
                   spansDays=field.hasEventsAt(zobj, date+1, events);
                   mayCreate=mayEdit and not events;
                   mayDelete=mayEdit and events;
                   day=date.day();
                   dayString=date.strftime('%Y/%m/%d')"
             style="date.isCurrentDay() and 'font-weight:bold' or \
                                            'font-weight:normal'"
             class=":cssClasses"
             onmouseover=":mayEdit and 'this.getElementsByTagName(\
               %s)[0].style.visibility=%s' % (q('img'), q('visible')) or ''"
             onmouseout="mayEdit and 'this.getElementsByTagName(\
               %s)[0].style.visibility=%s' % (q('img'), q('hidden')) or ''">
          <span>:day</span>
          <span if="day == 1">:_('month_%s_short' % date.aMonth())"></span>
          <!-- Icon for adding an event -->
          <x if="mayCreate">
           <img class="clickable" style="visibility:hidden"
                var="info=field.getApplicableEventsTypesAt(zobj, date, \
                            allEventTypes, preComputed, True)"
                if="info['eventTypes']" src=":url('plus')"
                onclick=":'openEventPopup(%s, %s, %s, null, %s, %s)' % \
                 (q('new'), q(field.name), q(dayString), q(info['eventTypes']),\
                  q(info['message']))"/>
          </x>
          <!-- Icon for deleting an event -->
          <img if="mayDelete" class="clickable" style="visibility:hidden"
               src=":url('delete')"
               onclick=":'openEventPopup(%s, %s, %s, %s, null, null)' % \
                 (q('del'), q(field.name), q(dayString), q(str(spansDays)))"/>
          <!-- A single event is allowed for the moment -->
          <div if="events" var2="eventType=events[0]['eventType']">
           <span style="color: grey">:field.getEventName(zobj, \
                                                         eventType)"></span>
          </div>
          <!-- Events from other calendars -->
          <x if="otherCalendars"
             var2="otherEvents=field.getOtherEventsAt(zobj, date, \
                                                      otherCalendars)">
           <div style=":'color: %s; font-style: italic' % event['color']"
                for="event in otherEvents">:event['name']</div>
          </x>
          <!-- Additional info -->
          <x var="info=field.getAdditionalInfoAt(zobj, date, preComputed)"
             if="info">::info</x>
         </td>
        </x>
       </tr>
      </table>

      <!-- Popup for creating a calendar event -->
      <div var="prefix='%s_newEvent' % field.name;
                popupId=prefix + 'Popup'"
           id=":popupId" class="popup" align="center">
       <form id="prefix + 'Form'" method="post">
        <input type="hidden" name="fieldName" value=":field.name"/>
        <input type="hidden" name="month" value=":month"/>
        <input type="hidden" name="name" value=":field.name"/>
        <input type="hidden" name="action" value="Process"/>
        <input type="hidden" name="actionType" value="createEvent"/>
        <input type="hidden" name="day"/>

        <!-- Choose an event type -->
        <div align="center" style="margin-bottom: 3px">:_('which_event')"></div>
        <select name="eventType">
         <option value="">:_('choose_a_value')"></option>
         <option for="eventType in allEventTypes"
                 value=":eventType">:field.getEventName(zobj, eventType)">
         </option>
        </select><br/><br/>
        <!--Span the event on several days -->
        <div align="center" class="discreet" style="margin-bottom: 3px">
         <span>:_('event_span')"></span>
         <input type="text" size="3" name="eventSpan"/>
        </div>
        <input type="button"
               value=":_('object_save')"
               onclick=":'triggerCalendarEvent(%s, %s, %s, %s, \
                          %s_maxEventLength)' % (q('new'), q(ajaxHookId), \
                          q(field.name), q(objUrl), field.name)"/>
        <input type="button"
               value=":_('object_cancel')"
               onclick=":'closePopup(%s)' % q(popupId)"/>
       </form>
      </div>

      <!-- Popup for deleting a calendar event -->
      <div var="prefix='%s_delEvent' % field.name;
                popupId=prefix + 'Popup'"
           id=":popupId" class="popup" align="center">
       <form id=":prefix + 'Form'" method="post">
        <input type="hidden" name="fieldName" value=":field.name"/>
        <input type="hidden" name="month" value=":month"/>
        <input type="hidden" name="name" value=":field.name"/>
        <input type="hidden" name="action" value="Process"/>
        <input type="hidden" name="actionType" value="deleteEvent"/>
        <input type="hidden" name="day"/>

        <div align="center" style="margin-bottom: 5px">_('delete_confirm')">
        </div>

        <!-- Delete successive events ? -->
        <div class="discreet" style="margin-bottom: 10px"
             id=":prefix + 'DelNextEvent'">
          <input type="checkbox" name="deleteNext_cb"
                 id=":prefix + '_cb'"
                 onClick=":'toggleCheckbox(%s, %s)' % \
                           (q('%s_cb' % prefix), q('%s_hd' % prefix))"/>
          <input type="hidden" id=":prefix + '_hd'" name="deleteNext"/>
          <span>:_('del_next_events')"></span>
        </div>
        <input type="button" value=":_('yes')"
               onClick=":'triggerCalendarEvent(%s, %s, %s, %s)' % \
                 (q('del'), q(ajaxHookId), q(field.name), q(objUrl))"/>
        <input type="button" value=":_('no')"
               onclick=":'closePopup(%s)' % q(popupId)"/>
       </form>
      </div>
     </div>''')

    pxView = pxCell = Px('''
     <x var="defaultDate=field.getDefaultDate(zobj);
             x=req.set('month', defaultDate.strftime('%Y/%m'));
             x=req.set('fieldName', field.name)">:field.pxMonthView</x>''')

    pxEdit = pxSearch = ''

    def __init__(self, eventTypes, eventNameMethod=None, validator=None,
                 default=None, show='view', page='main', group=None,
                 layouts=None, move=0, specificReadPermission=False,
                 specificWritePermission=False, width=None, height=300,
                 colspan=1, master=None, masterValue=None, focus=False,
                 mapping=None, label=None, maxEventLength=50,
                 otherCalendars=None, additionalInfo=None, startDate=None,
                 endDate=None, defaultDate=None, preCompute=None,
                 applicableEvents=None):
        Field.__init__(self, validator, (0,1), default, show, page, group,
                       layouts, move, False, False, specificReadPermission,
                       specificWritePermission, width, height, None, colspan,
                       master, masterValue, focus, False, True, mapping, label,
                       None, None, None, None)
        # eventTypes can be a "static" list or tuple of strings that identify
        # the types of events that are supported by this calendar. It can also
        # be a method that computes such a "dynamic" list or tuple. When
        # specifying a static list, an i18n label will be generated for every
        # event type of the list. When specifying a dynamic list, you must also
        # give, in p_eventNameMethod, a method that will accept a single arg
        # (=one of the event types from your dynamic list) and return the "name"
        # of this event as it must be shown to the user.
        self.eventTypes = eventTypes
        self.eventNameMethod = eventNameMethod
        if (type(eventTypes) == types.FunctionType) and not eventNameMethod:
            raise Exception("When param 'eventTypes' is a method, you must " \
                            "give another method in param 'eventNameMethod'.")
        # It is not possible to create events that span more days than
        # maxEventLength.
        self.maxEventLength = maxEventLength
        # When displaying a given month for this agenda, one may want to
        # pre-compute, once for the whole month, some information that will then
        # be given as arg for other methods specified in subsequent parameters.
        # This mechanism exists for performance reasons, to avoid recomputing
        # this global information several times. If you specify a method in
        # p_preCompute, it will be called every time a given month is shown, and
        # will receive 2 args: the first day of the currently shown month (as a
        # DateTime instance) and the grid of all shown dates (as a list of lists
        # of DateTime instances, one sub-list by row in the month view). This
        # grid may hold a little more than dates of the current month.
        # Subsequently, the return of your method will be given as arg to other
        # methods that you may specify as args of other parameters of this
        # Calendar class (see comments below).
        self.preCompute = preCompute
        # If a method is specified in the following parameters, it must accept
        # a single arg (the result of self.preCompute) and must return a list of
        # calendars whose events must be shown within this agenda.
        # Every element in this list must be a sub-list [object, name, color]
        # (not a tuple):
        # - object must refer to the other object on which the other calendar
        #   field is defined;
        # - name is the name of the field on this object that stores the
        #   calendar;
        # - color must be a string containing the HTML color (including the
        #   leading "#" when relevant) into which events of the calendar must
        #   appear.
        self.otherCalendars = otherCalendars
        # One may want to add, day by day, custom information in the calendar.
        # When a method is given in p_additionalInfo, for every cell of the
        # month view, this method will be called with 2 args: the cell's date
        # and the result of self.preCompute. The method's result (a string that
        # can hold text or a chunk of XHTML) will be inserted in the cell.
        self.additionalInfo = additionalInfo
        # One may limit event encoding and viewing to some period of time,
        # via p_startDate and p_endDate. Those parameters, if given, must hold
        # methods accepting no arg and returning a Zope DateTime instance. The
        # startDate and endDate will be converted to UTC at 00.00.
        self.startDate = startDate
        self.endDate = endDate
        # If a default date is specified, it must be a method accepting no arg
        # and returning a DateTime instance. As soon as the calendar is shown,
        # the month where this date is included will be shown. If not default
        # date is specified, it will be 'now' at the moment the calendar is
        # shown.
        self.defaultDate = defaultDate
        # For a specific day, all event types may not be applicable. If this is
        # the case, one may specify here a method that defines, for a given day,
        # a sub-set of all event types. This method must accept 3 args: the day
        # in question (as a DateTime instance), the list of all event types,
        # which is a copy of the (possibly computed) self.eventTypes) and
        # the result of calling self.preCompute. The method must modify
        # the 2nd arg and remove from it potentially not applicable events.
        # This method can also return a message, that will be shown to the user
        # for explaining him why he can, for this day, only create events of a
        # sub-set of the possible event types (or even no event at all).
        self.applicableEvents = applicableEvents

    def getPreComputedInfo(self, obj, monthDayOne, grid):
        '''Returns the result of calling self.preComputed, or None if no such
           method exists.'''
        if self.preCompute:
            return self.preCompute(obj.appy(), monthDayOne, grid)

    def getSiblingMonth(self, month, prevNext):
        '''Gets the next or previous month (depending of p_prevNext) relative
           to p_month.'''
        dayOne = DateTime('%s/01 UTC' % month)
        if prevNext == 'previous':
            refDate = dayOne - 1
        elif prevNext == 'next':
            refDate = dayOne + 33
        return refDate.strftime('%Y/%m')

    weekDays = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    def getNamesOfDays(self, obj, short=True):
        res = []
        for day in self.weekDays:
            if short:
                suffix = '_short'
            else:
                suffix = ''
            res.append(obj.translate('day_%s%s' % (day, suffix)))
        return res

    def getMonthGrid(self, month):
        '''Creates a list of lists of DateTime objects representing the calendar
           grid to render for a given p_month.'''
        # Month is a string "YYYY/mm".
        currentDay = DateTime('%s/01 UTC' % month)
        currentMonth = currentDay.month()
        res = [[]]
        dayOneNb = currentDay.dow() or 7 # This way, Sunday is 7 and not 0.
        if dayOneNb != 1:
            previousDate = DateTime(currentDay)
            # If the 1st day of the month is not a Monday, start the row with
            # the last days of the previous month.
            for i in range(1, dayOneNb):
                previousDate = previousDate - 1
                res[0].insert(0, previousDate)
        finished = False
        while not finished:
            # Insert currentDay in the grid
            if len(res[-1]) == 7:
                # Create a new row
                res.append([currentDay])
            else:
                res[-1].append(currentDay)
            currentDay = currentDay + 1
            if currentDay.month() != currentMonth:
                finished = True
        # Complete, if needed, the last row with the first days of the next
        # month.
        if len(res[-1]) != 7:
            while len(res[-1]) != 7:
                res[-1].append(currentDay)
                currentDay = currentDay + 1
        return res

    def getOtherCalendars(self, obj, preComputed):
        '''Returns the list of other calendars whose events must also be shown
           on this calendar.'''
        if self.otherCalendars:
            res = self.otherCalendars(obj.appy(), preComputed)
            # Replace field names with field objects
            for i in range(len(res)):
                res[i][1] = res[i][0].getField(res[i][1])
            return res

    def getAdditionalInfoAt(self, obj, date, preComputed):
        '''If the user has specified a method in self.additionalInfo, we call
           it for displaying this additional info in the calendar, at some
           p_date.'''
        if not self.additionalInfo: return
        return self.additionalInfo(obj.appy(), date, preComputed)

    def getEventTypes(self, obj):
        '''Returns the (dynamic or static) event types as defined in
           self.eventTypes.'''
        if type(self.eventTypes) == types.FunctionType:
            return self.eventTypes(obj.appy())
        else:
            return self.eventTypes

    def getApplicableEventsTypesAt(self, obj, date, allEventTypes, preComputed,
                                   forBrowser=False):
        '''Returns the event types that are applicable at a given p_date. More
           precisely, it returns an object with 2 attributes:
           * "events" is the list of applicable event types;
           * "message", not empty if some event types are not applicable,
                        contains a message explaining those event types are
                        not applicable.
        '''
        if not self.applicableEvents:
            eventTypes = allEventTypes
            message = None
        else:
            eventTypes = allEventTypes[:]
            message = self.applicableEvents(obj.appy(), date, eventTypes,
                                            preComputed)
        res = Object(eventTypes=eventTypes, message=message)
        if forBrowser:
            res.eventTypes = ','.join(res.eventTypes)
            if not res.message:
                res.message = ''
            else:
                res.message = obj.formatText(res.message, format='js')
            return res.__dict__
        return res

    def getEventsAt(self, obj, date, asDict=True):
        '''Returns the list of events that exist at some p_date (=day).'''
        obj = obj.o # Ensure p_obj is not a wrapper.
        if not hasattr(obj.aq_base, self.name): return
        years = getattr(obj, self.name)
        year = date.year()
        if year not in years: return
        months = years[year]
        month = date.month()
        if month not in months: return
        days = months[month]
        day = date.day()
        if day not in days: return
        if asDict:
            res = [e.__dict__ for e in days[day]]
        else:
            res = days[day]
        return res

    def getEventTypeAt(self, obj, date):
        '''Returns the event type of the first event defined at p_day, or None
           if unspecified.'''
        events = self.getEventsAt(obj, date, asDict=False)
        if not events: return
        return events[0].eventType

    def getEventsByType(self, obj, eventType, minDate=None, maxDate=None,
                        sorted=True, groupSpanned=False):
        '''Returns all the events of a given p_eventType. If p_eventType is
           None, it returns events of all types. The return value is a list of
           2-tuples whose 1st elem is a DateTime instance and whose 2nd elem is
           the event.
           If p_sorted is True, the list is sorted in chronological order. Else,
           the order is random, but the result is computed faster.
           If p_minDate and/or p_maxDate is/are specified, it restricts the
           search interval accordingly.
           If p_groupSpanned is True, events spanned on several days are
           grouped into a single event. In this case, tuples in the result
           are 3-tuples: (DateTime_startDate, DateTime_endDate, event).
        '''
        # Prevent wrong combinations of parameters
        if groupSpanned and not sorted:
            raise Exception('Events must be sorted if you want to get ' \
                            'spanned events to be grouped.')
        obj = obj.o # Ensure p_obj is not a wrapper.
        res = []
        if not hasattr(obj, self.name): return res
        # Compute "min" and "max" tuples
        if minDate:
            minYear = minDate.year()
            minMonth = (minYear, minDate.month())
            minDay = (minYear, minDate.month(), minDate.day())
        if maxDate:
            maxYear = maxDate.year()
            maxMonth = (maxYear, maxDate.month())
            maxDay = (maxYear, maxDate.month(), maxDate.day())
        # Browse years
        years = getattr(obj, self.name)
        for year in years.keys():
            # Don't take this year into account if outside interval
            if minDate and (year < minYear): continue
            if maxDate and (year > maxYear): continue
            months = years[year]
            # Browse this year's months
            for month in months.keys():
                # Don't take this month into account if outside interval
                thisMonth = (year, month)
                if minDate and (thisMonth < minMonth): continue
                if maxDate and (thisMonth > maxMonth): continue
                days = months[month]
                # Browse this month's days
                for day in days.keys():
                    # Don't take this day into account if outside interval
                    thisDay = (year, month, day)
                    if minDate and (thisDay < minDay): continue
                    if maxDate and (thisDay > maxDay): continue
                    events = days[day]
                    # Browse this day's events
                    for event in events:
                        # Filter unwanted events
                        if eventType and (event.eventType != eventType):
                            continue
                        # We have found a event.
                        date = DateTime('%d/%d/%d UTC' % (year, month, day))
                        if groupSpanned:
                            singleRes = [date, None, event]
                        else:
                            singleRes = (date, event)
                        res.append(singleRes)
        # Sort the result if required
        if sorted: res.sort(key=lambda x: x[0])
        # Group events spanned on several days if required
        if groupSpanned:
            # Browse events in reverse order and merge them when appropriate
            i = len(res) - 1
            while i > 0:
                currentDate = res[i][0]
                lastDate = res[i][1]
                previousDate = res[i-1][0]
                currentType = res[i][2].eventType
                previousType = res[i-1][2].eventType
                if (previousDate == (currentDate-1)) and \
                   (previousType == currentType):
                    # A merge is needed
                    del res[i]
                    res[i-1][1] = lastDate or currentDate
                i -= 1
        return res

    def hasEventsAt(self, obj, date, otherEvents):
        '''Returns True if, at p_date, an event is found of the same type as
           p_otherEvents.'''
        if not otherEvents: return False
        events = self.getEventsAt(obj, date, asDict=False)
        if not events: return False
        return events[0].eventType == otherEvents[0]['eventType']

    def getOtherEventsAt(self, obj, date, otherCalendars):
        '''Gets events that are defined in p_otherCalendars at some p_date.'''
        res = []
        for o, field, color in otherCalendars:
            events = field.getEventsAt(o.o, date, asDict=False)
            if events:
                eventType = events[0].eventType
                eventName = field.getEventName(o.o, eventType)
                info = Object(name=eventName, color=color)
                res.append(info.__dict__)
        return res

    def getEventName(self, obj, eventType):
        '''Gets the name of the event corresponding to p_eventType as it must
           appear to the user.'''
        if self.eventNameMethod:
            return self.eventNameMethod(obj.appy(), eventType)
        else:
            return obj.translate('%s_event_%s' % (self.labelId, eventType))

    def getStartDate(self, obj):
        '''Get the start date for this calendar if defined.'''
        if self.startDate:
            d = self.startDate(obj.appy())
            # Return the start date without hour, in UTC.
            return DateTime('%d/%d/%d UTC' % (d.year(), d.month(), d.day()))

    def getEndDate(self, obj):
        '''Get the end date for this calendar if defined.'''
        if self.endDate:
            d = self.endDate(obj.appy())
            # Return the end date without hour, in UTC.
            return DateTime('%d/%d/%d UTC' % (d.year(), d.month(), d.day()))

    def getDefaultDate(self, obj):
        '''Get the default date that must appear as soon as the calendar is
           shown.'''
        if self.defaultDate:
            return self.defaultDate(obj.appy())
        else:
            return DateTime() # Now

    def createEvent(self, obj, date, eventType=None, eventSpan=None,
                    handleEventSpan=True):
        '''Create a new event in the calendar, at some p_date (day).
           If p_eventType is given, it is used; else, rq['eventType'] is used.
           If p_handleEventSpan is True, we will use p_eventSpan (or
           rq["eventSpan"] if p_eventSpan is not given) and also
           create the same event for successive days.'''
        obj = obj.o # Ensure p_obj is not a wrapper.
        rq = obj.REQUEST
        # Get values from parameters
        if not eventType: eventType = rq['eventType']
        if handleEventSpan and not eventSpan:
            eventSpan = rq.get('eventSpan', None)
        # Split the p_date into separate parts
        year, month, day = date.year(), date.month(), date.day()
        # Check that the "preferences" dict exists or not.
        if not hasattr(obj.aq_base, self.name):
            # 1st level: create a IOBTree whose keys are years.
            setattr(obj, self.name, IOBTree())
        yearsDict = getattr(obj, self.name)
        # Get the sub-dict storing months for a given year
        if year in yearsDict:
            monthsDict = yearsDict[year]
        else:
            yearsDict[year] = monthsDict = IOBTree()
        # Get the sub-dict storing days of a given month
        if month in monthsDict:
            daysDict = monthsDict[month]
        else:
            monthsDict[month] = daysDict = IOBTree()
        # Get the list of events for a given day
        if day in daysDict:
            events = daysDict[day]
        else:
            daysDict[day] = events = PersistentList()
        # Create and store the event, excepted if an event already exists.
        if not events:
            event = Object(eventType=eventType)
            events.append(event)
        # Span the event on the successive days if required
        if handleEventSpan and eventSpan:
            nbOfDays = min(int(eventSpan), self.maxEventLength)
            for i in range(nbOfDays):
                date = date + 1
                self.createEvent(obj, date, handleEventSpan=False)

    def deleteEvent(self, obj, date, handleEventSpan=True):
        '''Deletes an event. It actually deletes all events at p_date.
           If p_handleEventSpan is True, we will use rq["deleteNext"] to
           delete successive events, too.'''
        obj = obj.o # Ensure p_obj is not a wrapper.
        if not self.getEventsAt(obj, date): return
        daysDict = getattr(obj, self.name)[date.year()][date.month()]
        # Remember events, in case we must delete similar ones for next days.
        events = self.getEventsAt(obj, date)
        del daysDict[date.day()]
        rq = obj.REQUEST
        if handleEventSpan and rq.has_key('deleteNext') and \
           (rq['deleteNext'] == 'True'):
            while True:
                date = date + 1
                if self.hasEventsAt(obj, date, events):
                    self.deleteEvent(obj, date, handleEventSpan=False)
                else:
                    break

    def process(self, obj):
        '''Processes an action coming from the calendar widget, ie, the creation
           or deletion of a calendar event.'''
        rq = obj.REQUEST
        action = rq['actionType']
        # Get the date for this action
        if action == 'createEvent':
            return self.createEvent(obj, DateTime(rq['day']))
        elif action == 'deleteEvent':
            return self.deleteEvent(obj, DateTime(rq['day']))

    def getCellStyle(self, obj, date, today):
        '''What CSS classes must apply to the table cell representing p_date
           in the calendar?'''
        res = []
        # We must distinguish between past and future dates.
        if date < today:
            res.append('even')
        else:
            res.append('odd')
        # Week-end days must have a specific style.
        if date.aDay() in ('Sat', 'Sun'):
            res.append('cellDashed')
        return ' '.join(res)
# ------------------------------------------------------------------------------
