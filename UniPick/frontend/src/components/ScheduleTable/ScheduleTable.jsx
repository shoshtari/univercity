import { Box, Tabs, Tab, Typography } from "@mui/material";
import { useMemo, useState } from "react";
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

const GRID_HEADER_COL_WIDTH = "90px";
const GRID_HEADER_ROW_HEIGHT = "44px";
const GRID_ROW_HEIGHT = "110px";

function ScheduleTable({ courses, pendingCourse, toggleCourse }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);

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

  const selectedDay = DAYS[selectedDayIndex];
  const selectedDayKey = DAY_MAP[selectedDay];
  const selectedDayCourses = dayCourses[selectedDayKey] || [];
  const selectedDayPendingCourses = pendingCourse?.courseTimes
    ?.filter((t) => t.weekday === selectedDayKey)
    ?.map((time) => ({
      start: timeToHour(time.start),
      end: timeToHour(time.end),
    })) || [];

  // Mobile vertical agenda view
  if (isMobile) {
    return (
      <Box sx={{ width: "100%" }}>
        {/* Day selector tabs */}
        <Tabs
          value={selectedDayIndex}
          onChange={(_, v) => setSelectedDayIndex(v)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            mb: 2,
            borderBottom: 1,
            borderColor: "divider",
            minHeight: 48,
            "& .MuiTab-root": {
              minHeight: 48,
              textTransform: "none",
              fontSize: 13,
              fontWeight: 500,
              px: 1,
              minWidth: 0,
              flexShrink: 1,
              whiteSpace: "nowrap",
            },
            "& .MuiTabs-indicator": {
              height: 3,
              borderRadius: "3px 3px 0 0",
            },
          }}
        >
          {DAYS.map((day) => (
            <Tab key={day} label={DAY_PERSIAN_MAP[day]} />
          ))}
        </Tabs>

        {/* Vertical agenda for selected day */}
        <Box
          sx={{
            border: "1px solid #ddd",
            borderRadius: 1,
            overflow: "hidden",
            backgroundColor: "background.paper",
          }}
        >
          {Array.from({ length: TOTAL_HOURS }).map((_, i) => {
            const hour = SCHEDULE_START_HOUR + i;
            const hourStart = hour;
            const hourEnd = hour + 1;

            // Find courses in this hour
            const coursesInHour = selectedDayCourses.filter(
              (c) => c.start < hourEnd && c.end > hourStart
            );
            const pendingInHour = selectedDayPendingCourses.filter(
              (c) => c.start < hourEnd && c.end > hourStart
            );

            return (
              <Box
                key={i}
                sx={{
                  borderBottom: i < TOTAL_HOURS - 1 ? "1px solid #eee" : "none",
                  minHeight: 70,
                  position: "relative",
                  px: 2,
                  py: 1,
                }}
              >
                {/* Hour label */}
                <Box
                  sx={{
                    position: "absolute",
                    left: 0,
                    top: 0,
                    bottom: 0,
                    width: 50,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 12,
                    fontWeight: 500,
                    color: "text.secondary",
                    backgroundColor: "background.default",
                    borderRight: "1px solid #eee",
                    zIndex: 1,
                  }}
                >
                  {hour}:00
                </Box>

                {/* Courses in this hour */}
                <Box
                  sx={{
                    ml: 56,
                    display: "flex",
                    flexDirection: "column",
                    gap: 1,
                    minHeight: "100%",
                  }}
                >
                  {coursesInHour.map((c) => (
                    <ScheduleTableCell
                      key={`${c.course.id}-${hour}`}
                      course={c.course}
                      toggleCourse={toggleCourse}
                      state={SCHEDULE_CELL_STATE.SELECTED}
                      variant1="body2"
                      variant2="caption"
                      isMobile={isMobile}
                      clamp={2}
                      styleOverrides={{
                        borderRadius: 1,
                      }}
                    />
                  ))}
                  {pendingInHour.map((c, idx) => (
                    <ScheduleTableCell
                      key={`${pendingCourse.id}-${hour}-${idx}`}
                      course={pendingCourse}
                      toggleCourse={toggleCourse}
                      state={SCHEDULE_CELL_STATE.PENDING}
                      variant1="body2"
                      variant2="caption"
                      isMobile={isMobile}
                      clamp={2}
                      styleOverrides={{
                        borderRadius: 1,
                      }}
                    />
                  ))}
                  {coursesInHour.length === 0 && pendingInHour.length === 0 && (
                    <Box sx={{ flex: 1 }} />
                  )}
                </Box>
              </Box>
            );
          })}
        </Box>
      </Box>
    );
  }

  // Desktop grid view
  const DAY_COL_MIN_WIDTH = "100px";
  const gridTemplateColumns = `repeat(${TOTAL_HOURS}, minmax(${DAY_COL_MIN_WIDTH}, 1fr)) ${GRID_HEADER_COL_WIDTH}`;
  return (
    <Box
      sx={{
        overflowX: "auto",
        width: "100%",
        webkitOverflowScrolling: "touch",
      }}
    >
      <Box
        sx={{
          display: "grid",
          gridTemplateRows: `${GRID_HEADER_ROW_HEIGHT} repeat(${DAYS.length}, ${GRID_ROW_HEIGHT})`,
          gridTemplateColumns: gridTemplateColumns,
          border: "1px solid #ddd",
          minWidth: "max-content",
        }}
      >
        {/* Hour headers */}
        {Array.from({ length: TOTAL_HOURS }).map((_, i) => {
          const hour = SCHEDULE_START_HOUR + i;
          return (
            <Box
              key={i}
              sx={{
                borderRight: "1px solid #eee",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                fontSize: 13,
                whiteSpace: "nowrap",
                fontWeight: 500,
                color: "text.secondary",
              }}
            >
              {hour}:00
            </Box>
          );
        })}

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
              key={`${i.course.id}-${i.start}-${i.end}`}
              course={i.course}
              toggleCourse={toggleCourse}
              state={SCHEDULE_CELL_STATE.SELECTED}
              start={i.start}
              end={i.end}
              isMobile={isMobile}
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
              return null;

            const { left, width } = getLeftAndWidth(start, end);
            return (
              <ScheduleTableCell
                key={`${pendingCourse.id}-${idx}`}
                course={pendingCourse}
                toggleCourse={toggleCourse}
                state={SCHEDULE_CELL_STATE.PENDING}
                start={start}
                end={end}
                isMobile={isMobile}
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
          fontSize: 14,
          minWidth: "90px",
        }}
      >
        {DAY_PERSIAN_MAP[day]}
      </Box>
    </>
  );
}