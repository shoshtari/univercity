import datetime
import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class CourseTime:
    weekday: str
    start: datetime.time
    end: datetime.time

    @classmethod
    def parse_json(cls, marshalled: str) -> list["CourseTime"]:
        unmarshalled = json.loads(marshalled)
        return [
            cls(
                weekday=i["weekday"],
                start=datetime.datetime.strptime(i["start"], "%H:%M").time(),
                end=datetime.datetime.strptime(i["end"], "%H:%M").time(),
            )
            for i in unmarshalled
        ]


@dataclass
class Course:
    id: int
    name: str
    code: str
    instructor: str
    group: str
    courseTimes: list[CourseTime]
    units: int
    exam_date: str
    major: str
    classroom: str
    prerequisite_corequisite: Optional[str]
    semester: str
    update_date: str
