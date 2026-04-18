import { Box } from "@mui/material";
import { useMemo } from "react";
import ScheduleTableCell from "./ScheduleTableCell";
import {ScheduleTableHeaderColumnWidth, ScheduleTableRowHeight, ScheduleTableHeaderRowHeight} from "../../configs/sizes";
import {
  DAYS,
  TOTAL_HOURS,
  timeToHour,
  DAY_MAP,
  DAY_PERSIAN_MAP,
  START_HOUR,
  END_HOUR,
} from "./helpers";

function ScheduleTable({ courses, pendingCourse, toggleCourse }) {
  const dayCourses = useMemo(() => {
    const ans = {};
    for (const course of courses) {
      for (const t of course.courseTimes) {
        ans[t.weekday] = ans[t.weekday] || [];
        ans[t.weekday].push({
          course,
          start: timeToHour(t.start),
          end: timeToHour(t.end),
        });
      }
    }
    return ans;
  }, [courses]);

  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateRows: `${ScheduleTableHeaderRowHeight} repeat(${DAYS.length}, ${ScheduleTableRowHeight})`,
        gridTemplateColumns: `repeat(${TOTAL_HOURS}, 1fr) ${ScheduleTableHeaderColumnWidth}`,
        border: "1px solid #ddd",
      }}
    >
      {/* Hour headers */}
      {Array.from({ length: TOTAL_HOURS }).map((_, i) => (
        <Box
          key={i}
          sx={{
            borderRight: "1px solid #eee",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            fontSize: 12,
          }}
        >
          {END_HOUR - i - 1}:00
        </Box>
      ))}

      <Box />
      {/* Day rows */}
      {DAYS.map((day, rowIndex) => (
        <DayRow
          key={day}
          day={day}
          courses={dayCourses[DAY_MAP[day]] || []}
          pendingCourse={pendingCourse}
          toggleCourse={toggleCourse}
        />
      ))}
    </Box>
  );
}

export default ScheduleTable;
function DayRow({ day, courses, pendingCourse, toggleCourse }) {
  return (
    <>
      <Box
        sx={{
          gridColumn: `1 / span ${TOTAL_HOURS}`,
          position: "relative",
          borderTop: "1px solid #eee",
        }}
      >
        {courses.map((i) => {
          return (
            <ScheduleTableCell
              key={`${i.course.id}`}
              course={i.course}
              toggleCourse={toggleCourse}
              start={i.start}
              end={i.end}
              state="selected"
            />
          );
        })}
        {pendingCourse?.courseTimes
          .filter((t) => t.weekday === DAY_MAP[day])
          .map((time, idx) => {
            const start = timeToHour(time.start);
            const end = timeToHour(time.end);
            if (courses.some((c) => c.course.id === pendingCourse.id)) return null; // don't show pending course if it's already selected

            return (
              <ScheduleTableCell
                key={`${pendingCourse.id}-${idx}`}
                course={pendingCourse}
                toggleCourse={toggleCourse}
                start={start}
                end={end}
                state="pending"
              />
            );
          })}
      </Box>

      {/* Day label */}
      <Box
        sx={{
          borderTop: "1px solid #eee",
          borderLeft: "1px solid #eee",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontWeight: 500,
        }}
      >
        {DAY_PERSIAN_MAP[day]}
      </Box>
    </>
  );
}
