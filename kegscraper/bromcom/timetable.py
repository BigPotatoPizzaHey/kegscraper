"""
Timetable Dataclasses for bromcom
"""
from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass


@dataclass
class WeekDate:
    """
    A dataclass representing a start of a week to be used with the bromcom timetable.
    """
    term_i: int
    week_i: int
    date: datetime

@dataclass
class Lesson:
    """
    A dataclass representing a lesson in the bromcom timetable
    """
    period: int
    subject: str
    class_name: str
    room: str
    teacher: str
    # There is also a teacher id provided, but I am unaware of any use
    # A week id is also provided, but I am unaware of any use

    start: datetime
    end: datetime

    color: str = None
