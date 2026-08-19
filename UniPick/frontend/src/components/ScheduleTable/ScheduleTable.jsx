import { Box } from "@mui/material";
import { useMemo } from "react";
import { useMediaQuery, useTheme } from "@mui/material";
import ScheduleTableCell from "./ScheduleTableCell";
import { getLeftAndWidth, timeToHour } from "./helpers";
import {
  ScheduleTableHeaderColumnWidth,
  ScheduleTableRowHeight,
  ScheduleTableHeaderRowHeight,
  ScheduleCellInset,
} from "../../configs/sizes";
import {
  DAYS,
  SCHEDULE_TOTAL_HOURS as TOTAL_HOURS,
  DAY_MAP,
  DAY_PERSIAN_MAP,
  SCHEDULE_START_HOUR,
  SCHEDULE_END_HOUR,
  SCHEDULE_CELL_STATE,
} from "../../configs/schedule";

function ScheduleTable({ courses, pendingCourse, toggleCourse }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

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

  const gridTemplateColumns = `repeat(${TOTAL_HOURS}, 1fr) ${ScheduleTableHeaderColumnWidth}`;

  return (
    <Box
      sx={{
        overflowX: isMobile ? "auto" : "hidden",
        width: "100%",
        "-webkit-overflow-scrolling": "touch",
      }}
    >
      <Box
        sx={{
          display: "grid",
          gridTemplateRows: `${ScheduleTableHeaderRowHeight} repeat(${DAYS.length}, ${ScheduleTableRowHeight})`,
          gridTemplateColumns: gridTemplateColumns,
          border: "1px solid #ddd",
          minWidth: isMobile ? "max-content" : "100%",
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
              fontSize: { xs: 10, sm: 11, md: 12 },
              whiteSpace: "nowrap",
            }}
          >
            {SCHEDULE_END_HOUR - i - 1}:00
          </Box>
        ))}

        <Box />
        {/* Day rows */}
        {DAYS.map((day) => (
          <DayRow
            key={day}
            day={day}
            courses={dayCourses[DAY_MAP[day]] || []}
            pendingCourse={pendingCourse}
            toggleCourse={toggleCourse}
            isMobile={isMobile}
          />
        ))}
      </Box>
    </Box>
  );
}

export default ScheduleTable;

function DayRow({ day, courses, pendingCourse, toggleCourse, isMobile }) {
  return (
    <>
      <Box
        sx={{
          gridColumn: `1 / span ${TOTAL_HOURS}`,
          position: "relative",
          borderTop: "1px solid #eee",
          minHeight: ScheduleTableRowHeight,
        }}
      >
        {courses.map((i) => {
          const { left, width } = getLeftAndWidth(i.start, i.end);
          return (
            <ScheduleTableCell
              key={`${i.course.id}`}
              course={i.course}
              toggleCourse={toggleCourse}
              state={SCHEDULE_CELL_STATE.SELECTED}
              start={i.start}
              end={i.end}
              styleOverrides={{
                position: "absolute",
                left: `${left}%`,
                width: `${width}%`,
                top: ScheduleCellInset,
                bottom: ScheduleCellInset,
                clamp: 2,
                cursor: "pointer",
                "&:hover": {
                  opacity: 1,
                  zIndex: 2,
                  boxShadow: 3,
                },
              }}
            />
          );
        })}
        {pendingCourse?.courseTimes
          .filter((t) => t.weekday === DAY_MAP[day])
          .map((time, idx) => {
            const start = timeToHour(time.start);
            const end = timeToHour(time.end);
            if (courses.some((c) => c.course.id === pendingCourse.id))
              return null; // don't show pending course if it's already selected

            const { left, width } = getLeftAndWidth(start, end);
            return (
              <ScheduleTableCell
                key={`${pendingCourse.id}-${idx}`}
                course={pendingCourse}
                toggleCourse={toggleCourse}
                state={SCHEDULE_CELL_STATE.PENDING}
                start={start}
                end={end}
                styleOverrides={{
                  position: "absolute",
                  left: `${left}%`,
                  width: `${width}%`,
                  top: ScheduleCellInset,
                  bottom: ScheduleCellInset,
                  clamp: 2,
                }}
              />
            );
          })}
      </Box>

      <Box
        sx={{
          borderTop: "1px solid #eee",
          borderLeft: "1px solid #eee",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontWeight: 500,
          fontSize: { xs: 12, sm: 13, md: 14 },
        }}
      >
        {DAY_PERSIAN_MAP[day]}
      </Box>
    </>
  );
}