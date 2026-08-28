"""Turn relative day offsets into real dates for a chosen Flex session.

The course ships day offsets, not dates, and this is the file that explains
why in one place.

Six of the eight Flex sessions run Monday to Saturday across exactly 55 days.
That shape gives seven Sunday deadlines, on days 7, 14, 21, 28, 35, 42 and 49,
and a six-day final block on days 50 to 55. Week 8 contains no Sunday, which is
the whole reason the course is seven instructional weeks and a final block
rather than eight weeks.

Both Spring Flex I sessions break that. They start on a Tuesday, run 61 days,
and have Spring Break inside them. A course shell with dates baked in is wrong
for two sessions out of eight and nobody notices until a student misses a
deadline.

So dates are computed at build time from a session name, and the same content
builds correctly for any session.

The session dates below are placeholders derived from the published calendar
shape, not transcribed from a specific academic year's calendar, because those
are published per year and change. Set them from the registrar's calendar
before a term depends on them. `--session custom --start YYYY-MM-DD` takes a
start date directly.
"""

from __future__ import annotations

import datetime as dt

# Each session: the weekday it starts on, and how many days it runs.
# `start` is filled in per academic year and is deliberately not hardcoded to
# one year here.
SESSIONS: dict[str, dict] = {
    "fall-flex-1":   {"weekday": 0, "days": 55, "note": "Monday start, standard shape"},
    "fall-flex-2":   {"weekday": 0, "days": 55, "note": "Monday start, standard shape"},
    "spring-flex-1": {"weekday": 1, "days": 61,
                      "note": "Tuesday start, 61 days, Spring Break inside"},
    "spring-flex-2": {"weekday": 0, "days": 55, "note": "Monday start, standard shape"},
    "summer-flex-1": {"weekday": 0, "days": 55, "note": "Monday start, standard shape"},
    "summer-flex-2": {"weekday": 0, "days": 55, "note": "Monday start, standard shape"},
}

# A build has to produce dates, and a demo has to be reproducible, so a build
# with no start date given uses the next occurrence of the session's start
# weekday after this reference Monday. Change it, or pass --start.
REFERENCE_MONDAY = dt.date(2027, 1, 18)


class DateMap:
    """Day offsets to timestamps, for one session."""

    def __init__(self, session: str = "fall-flex-2", start: dt.date | None = None,
                 deadline_hour: int = 23, deadline_minute: int = 59):
        if session not in SESSIONS and start is None:
            raise ValueError(
                f"Unknown session {session!r}. Known: {', '.join(sorted(SESSIONS))}. "
                f"Pass a start date instead if this is a session not listed here."
            )
        self.session = session
        self.spec = SESSIONS.get(session, {"weekday": 0, "days": 55, "note": "custom"})
        self.deadline_hour = deadline_hour
        self.deadline_minute = deadline_minute

        if start is None:
            offset = (self.spec["weekday"] - REFERENCE_MONDAY.weekday()) % 7
            start = REFERENCE_MONDAY + dt.timedelta(days=offset)
        self.start = start

    def date(self, day: int) -> dt.date:
        """Day 1 is the first day of the session."""
        if day < 1:
            raise ValueError(f"Day {day} is before the course starts.")
        return self.start + dt.timedelta(days=day - 1)

    def at(self, day: int, hour: int | None = None, minute: int | None = None) -> str:
        """An ISO timestamp Canvas will accept, at the deadline time by default."""
        moment = dt.datetime.combine(
            self.date(day),
            dt.time(self.deadline_hour if hour is None else hour,
                    self.deadline_minute if minute is None else minute),
        )
        return moment.strftime("%Y-%m-%dT%H:%M:%S")

    def describe(self) -> str:
        last = self.date(self.spec["days"])
        return (f"{self.start.isoformat()} to {last.isoformat()}, "
                f"{self.spec['days']} days, {self.spec['note']}")

    def deadlines(self) -> list[tuple[int, str]]:
        """The seven weekly deadlines, so a build can be eyeballed."""
        return [(day, self.date(day).strftime("%a %d %b %Y"))
                for day in (7, 14, 21, 28, 35, 42, 49)]


if __name__ == "__main__":  # pragma: no cover
    for name in sorted(SESSIONS):
        dates = DateMap(name)
        print(f"{name:16} {dates.describe()}")
        weekdays = {day: label.split()[0] for day, label in dates.deadlines()}
        odd = {d: w for d, w in weekdays.items() if w != "Sun"}
        print(f"                 weekly deadlines land on: "
              f"{'Sunday' if not odd else odd}")
