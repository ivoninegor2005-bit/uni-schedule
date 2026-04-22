from icalendar import Calendar, Event
from datetime import datetime

cal = Calendar()
cal.add("prodid", "-//Uni Schedule//RU")
cal.add("version", "2.0")

event = Event()
event.add("uid", "1")
event.add("dtstart", datetime(2026, 4, 22, 12, 0, 0))
event.add("dtend", datetime(2026, 4, 22, 13, 35, 0))
event.add("summary", "Методика обучения биологии")

cal.add_component(event)

with open("calendar.ics", "wb") as f:
    f.write(cal.to_ical())
