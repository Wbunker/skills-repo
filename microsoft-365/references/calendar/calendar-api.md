# Outlook Calendar API (Microsoft Graph)

Access Outlook Calendar via Microsoft Graph to create events, manage meetings,
check free/busy, and find meeting times.

## Permissions

| Scenario | Delegated | Application |
|----------|-----------|-------------|
| Read calendars | `Calendars.Read` | `Calendars.Read` |
| Read + write | `Calendars.ReadWrite` | `Calendars.ReadWrite` |
| Read free/busy only | `Calendars.ReadBasic` | `Calendars.ReadBasic.All` |
| Shared calendars (read) | `Calendars.Read.Shared` | — |
| Shared calendars (write) | `Calendars.ReadWrite.Shared` | — |

## Base Endpoints

```
GET  /me/calendar                                 # Default calendar
GET  /me/calendars                                # All calendars
GET  /me/events                                   # All events (all calendars)
GET  /me/calendar/events                          # Events in default calendar
GET  /me/calendars/{calendar-id}/events           # Events in specific calendar
POST /me/events                                   # Create event
GET  /users/{user-id}/events                      # Another user's events (app-only)
```

## List Events

```python
import asyncio
from msgraph import GraphServiceClient
from msgraph.generated.users.item.events.events_request_builder import (
    EventsRequestBuilder,
)
from kiota_abstractions.base_request_configuration import RequestConfiguration

async def list_upcoming_events(graph_client, top=10):
    query_params = EventsRequestBuilder.EventsRequestBuilderGetQueryParameters(
        select=["subject", "start", "end", "location", "attendees", "isOnlineMeeting"],
        top=top,
        order_by=["start/dateTime ASC"],
        filter="start/dateTime ge '2024-01-01T00:00:00Z'",
    )
    config = RequestConfiguration(query_parameters=query_params)
    events = await graph_client.me.events.get(request_configuration=config)
    return events.value
```

## List Events in a Date Range

```python
async def get_events_in_range(graph_client, start_dt: str, end_dt: str):
    """
    start_dt, end_dt: ISO 8601 strings, e.g. '2024-03-01T00:00:00Z'
    """
    query_params = EventsRequestBuilder.EventsRequestBuilderGetQueryParameters(
        select=["subject", "start", "end", "location", "organizer"],
        filter=f"start/dateTime ge '{start_dt}' and end/dateTime le '{end_dt}'",
        order_by=["start/dateTime ASC"],
    )
    config = RequestConfiguration(query_parameters=query_params)
    events = await graph_client.me.calendar_view.get(request_configuration=config)
    return events.value
```

**Prefer `/me/calendarView` for range queries** — it handles recurring events correctly
and returns individual occurrences of recurrences within the range.

```
GET /me/calendarView?startDateTime=2024-01-01T00:00:00Z&endDateTime=2024-01-31T23:59:59Z
```

## Create an Event

```python
from msgraph.generated.models.event import Event
from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.location import Location
from msgraph.generated.models.attendee import Attendee
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.attendee_type import AttendeeType

async def create_event(graph_client):
    event = Event(
        subject="Team Sync",
        body=ItemBody(
            content_type=BodyType.Html,
            content="<b>Agenda:</b><br>1. Updates<br>2. Q&A",
        ),
        start=DateTimeTimeZone(
            date_time="2024-06-15T14:00:00",
            time_zone="America/New_York",
        ),
        end=DateTimeTimeZone(
            date_time="2024-06-15T15:00:00",
            time_zone="America/New_York",
        ),
        location=Location(display_name="Conference Room A"),
        attendees=[
            Attendee(
                email_address=EmailAddress(
                    address="alice@example.com",
                    name="Alice",
                ),
                type=AttendeeType.Required,
            ),
            Attendee(
                email_address=EmailAddress(
                    address="bob@example.com",
                    name="Bob",
                ),
                type=AttendeeType.Optional,
            ),
        ],
        is_online_meeting=True,
        online_meeting_provider="teamsForBusiness",
        # Attendees receive email invitations automatically
        # response_requested=True (default)
    )
    created = await graph_client.me.events.post(event)
    return created
```

## Update an Event

```python
from msgraph.generated.models.event import Event
from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone

async def update_event(graph_client, event_id, new_subject=None, new_start=None, new_end=None):
    update = Event()
    if new_subject:
        update.subject = new_subject
    if new_start:
        update.start = DateTimeTimeZone(
            date_time=new_start,
            time_zone="UTC",
        )
    if new_end:
        update.end = DateTimeTimeZone(
            date_time=new_end,
            time_zone="UTC",
        )
    await graph_client.me.events.by_event_id(event_id).patch(update)
```

## Delete / Cancel an Event

```python
# Delete (no cancellation notice sent)
await graph_client.me.events.by_event_id(event_id).delete()

# Cancel (sends cancellation to attendees)
from msgraph.generated.users.item.events.item.cancel.cancel_post_request_body import (
    CancelPostRequestBody,
)
await graph_client.me.events.by_event_id(event_id).cancel.post(
    CancelPostRequestBody(comment="Meeting cancelled due to scheduling conflict.")
)
```

## Respond to Event Invitations

```python
from msgraph.generated.users.item.events.item.accept.accept_post_request_body import (
    AcceptPostRequestBody,
)

# Accept
await graph_client.me.events.by_event_id(event_id).accept.post(
    AcceptPostRequestBody(comment="Looking forward to it!", send_response=True)
)

# Tentatively accept
from msgraph.generated.users.item.events.item.tentatively_accept.tentatively_accept_post_request_body import (
    TentativelyAcceptPostRequestBody,
)
await graph_client.me.events.by_event_id(event_id).tentatively_accept.post(
    TentativelyAcceptPostRequestBody(send_response=True)
)

# Decline
from msgraph.generated.users.item.events.item.decline.decline_post_request_body import (
    DeclinePostRequestBody,
)
await graph_client.me.events.by_event_id(event_id).decline.post(
    DeclinePostRequestBody(comment="Sorry, I have a conflict.", send_response=True)
)
```

## Create a Recurring Event

```python
from msgraph.generated.models.recurrence_pattern import RecurrencePattern
from msgraph.generated.models.recurrence_pattern_type import RecurrencePatternType
from msgraph.generated.models.day_of_week import DayOfWeek
from msgraph.generated.models.recurrence_range import RecurrenceRange
from msgraph.generated.models.recurrence_range_type import RecurrenceRangeType
from msgraph.generated.models.patterned_recurrence import PatternedRecurrence
import datetime

event = Event(
    subject="Weekly Standup",
    start=DateTimeTimeZone(date_time="2024-06-17T09:00:00", time_zone="America/New_York"),
    end=DateTimeTimeZone(date_time="2024-06-17T09:30:00", time_zone="America/New_York"),
    recurrence=PatternedRecurrence(
        pattern=RecurrencePattern(
            type=RecurrencePatternType.Weekly,
            interval=1,
            days_of_week=[DayOfWeek.Monday],
        ),
        range=RecurrenceRange(
            type=RecurrenceRangeType.EndDate,
            start_date=datetime.date(2024, 6, 17),
            end_date=datetime.date(2024, 12, 31),
        ),
    ),
)
created = await graph_client.me.events.post(event)
```

## Get Free/Busy Information

```python
from msgraph.generated.users.item.calendar.get_schedule.get_schedule_post_request_body import (
    GetSchedulePostRequestBody,
)
from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone

async def get_free_busy(graph_client, user_emails, start_dt, end_dt):
    request_body = GetSchedulePostRequestBody(
        schedules=user_emails,  # List of email addresses
        start_time=DateTimeTimeZone(date_time=start_dt, time_zone="UTC"),
        end_time=DateTimeTimeZone(date_time=end_dt, time_zone="UTC"),
        availability_view_interval=30,  # Minutes per slot
    )
    result = await graph_client.me.calendar.get_schedule.post(request_body)
    return result.value
    # Each item has: .availability_view (string of 0=free, 1=tentative, 2=busy, 3=OOF, 4=elsewhere)
    # and .schedule_items (list of actual events)
```

## Find Meeting Times

```python
from msgraph.generated.users.item.find_meeting_times.find_meeting_times_post_request_body import (
    FindMeetingTimesPostRequestBody,
)
from msgraph.generated.models.attendee_base import AttendeeBase
from msgraph.generated.models.time_constraint import TimeConstraint
from msgraph.generated.models.time_slot import TimeSlot

async def find_meeting_times(graph_client, attendee_emails, duration_hours=1):
    attendees = [
        AttendeeBase(
            email_address=EmailAddress(address=email),
            type=AttendeeType.Required,
        )
        for email in attendee_emails
    ]

    request_body = FindMeetingTimesPostRequestBody(
        attendees=attendees,
        time_constraint=TimeConstraint(
            timeslots=[
                TimeSlot(
                    start=DateTimeTimeZone(date_time="2024-06-17T08:00:00", time_zone="UTC"),
                    end=DateTimeTimeZone(date_time="2024-06-17T18:00:00", time_zone="UTC"),
                )
            ]
        ),
        meeting_duration=f"PT{duration_hours}H",  # ISO 8601 duration
        max_candidates=5,
    )
    result = await graph_client.me.find_meeting_times.post(request_body)
    return result.meeting_time_suggestions
```

## Manage Multiple Calendars

```python
# List all calendars
calendars = await graph_client.me.calendars.get()

# Create a new calendar
from msgraph.generated.models.calendar import Calendar

new_cal = await graph_client.me.calendars.post(
    Calendar(name="Project Calendar", color="lightBlue")
)

# Add event to specific calendar
event = Event(subject="Project Kickoff", ...)
await graph_client.me.calendars.by_calendar_id(new_cal.id).events.post(event)
```

## Calendar Sharing / Permissions

```python
# Get calendar permissions (who it's shared with)
perms = await graph_client.me.calendar.calendar_permissions.get()
for perm in perms.value:
    print(perm.principal.email_address.address, perm.role)
    # role: 'none', 'freeBusyRead', 'limitedRead', 'read', 'readBasic',
    #       'readAndWrite', 'delegateWithoutPrivateEventAccess',
    #       'delegateWithPrivateEventAccess', 'custom'
```

## OData Tips for Events

```
# Only future events
$filter=start/dateTime ge '2024-01-01T00:00:00Z'

# Online meetings only
$filter=isOnlineMeeting eq true

# Events organized by a specific person
$filter=organizer/emailAddress/address eq 'boss@example.com'

# Expand attendees in response
$expand=attachments

# Select specific fields to reduce payload
$select=subject,start,end,location,attendees,onlineMeeting
```

## Event Response Status

When reading events with attendees, check response status:

```python
event = await graph_client.me.events.by_event_id(event_id).get()
for attendee in event.attendees:
    print(
        attendee.email_address.address,
        attendee.status.response,  # 'none', 'accepted', 'declined', 'tentativelyAccepted'
        attendee.status.time,
    )
```
