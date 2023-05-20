pip install icalendar

# imports
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime
from pathlib import Path
import os
import pytz
 
# init the calendar
cal = Calendar()

# Some properties are required to be compliant
cal.add('prodid', '-//My calendar product//example.com//')
cal.add('version', '2.0')

# Add subcomponents
event = Event()
event.add('name', 'Awesome Meeting')
event.add('description', 'Define the roadmap of our awesome project')
event.add('dtstart', datetime(2022, 1, 25, 8, 0, 0, tzinfo=pytz.utc))
event.add('dtend', datetime(2022, 1, 25, 10, 0, 0, tzinfo=pytz.utc))
 
# Add the organizer
organizer = vCalAddress('MAILTO:jdoe@example.com')
 
# Add parameters of the event
organizer.params['name'] = vText('John Doe')
organizer.params['role'] = vText('CEO')
event['organizer'] = organizer
event['location'] = vText('New York, USA')
 
event['uid'] = '2022125T111010/272356262376@example.com'
event.add('priority', 5)
attendee = vCalAddress('MAILTO:rdoe@example.com')
attendee.params['name'] = vText('Richard Roe')
attendee.params['role'] = vText('REQ-PARTICIPANT')
event.add('attendee', attendee, encode=0)
 
attendee = vCalAddress('MAILTO:jsmith@example.com')
attendee.params['name'] = vText('John Smith')
attendee.params['role'] = vText('REQ-PARTICIPANT')
event.add('attendee', attendee, encode=0)
 
# Add the event to the calendar
cal.add_component(event)

# Write to disk
directory = Path.cwd() / 'MyCalendar'
try:
   directory.mkdir(parents=True, exist_ok=False)
except FileExistsError:
   print("Folder already exists")
else:
   print("Folder was created")
 
f = open(os.path.join(directory, 'example.ics'), 'wb')
f.write(cal.to_ical())
f.close()

e = open('MyCalendar/example.ics', 'rb')
ecal = icalendar.Calendar.from_ical(e.read())
for component in ecal.walk():
   print(component.name)
e.close()


- Dans Django, exemple de code fontionnel avec icalendar :
```
cal = Calendar()
cal.add('prodid', '-//My calendar product//example.com//')
cal.add('version', '2.0')

event = Event()
event.add('name', 'Awesome Meeting')
event.add('description', 'Define the roadmap of our awesome project')
event.add('dtstart', datetime(2022, 1, 25, 8, 0, 0, tzinfo=pytz.utc))
event.add('dtend', datetime(2022, 1, 25, 10, 0, 0, tzinfo=pytz.utc))
cal.add_component(event)

#response = HttpResponse(mimetype="text/calendar")
#response['Content-Disposition'] = 'attachment; filename=%s.ics' % event.slug
f1 = ContentFile(cal.to_ical())
response = HttpResponse(f1,headers={"Content-Type": "text/calendar","Content-Disposition": 'attachment; filename="foo.ics"',},)
return response
```

- code fonctionnel avec ICS :
```
c = Cal()
e = Ev()
e.name = "My cool event"
e.begin = '2014-01-01 00:00:00'
c.events.add(e)
c.events
f1 = ContentFile(c.serialize())
response = HttpResponse(f1,headers={"Content-Type": "text/calendar","Content-Disposition": 'attachment; filename="foo.ics"',},)
return response
```
