
import { Box, Card, CardContent, Typography } from "@mui/material";
import { useMemo } from "react";
import ScheduleTableCell from "../ScheduleTable/ScheduleTableCell";

import { toGregorian, toJalaali } from "jalaali-js";

function jdateToInt(jdate) {
  const [jy, jm, jd] = jdate.split("-").map(Number);
  const { gy, gm, gd } = toGregorian(jy, jm, jd);
  const date = Date.UTC(gy, gm, gd);
  const ans = Math.floor(date / 86400000);
  return ans;
}
function intToJdate(dayNumber) {
  const date = new Date(dayNumber * 86400000);
  const { jy, jm, jd } = toJalaali(
    date.getUTCFullYear(),
    date.getUTCMonth() + 1,
    date.getUTCDate(),
  );

  return `${jy}-${String(jm).padStart(2, "0")}-${String(jd).padStart(2, "0")}`;
}

function ExamSchedule({ courses }) {
  const { maxDay, minDay, dayToCourse } = useMemo(() => {
    let minDay = Number.MAX_SAFE_INTEGER,
      maxDay = 0,
      dayToCourse = {};

    for (const course of courses) {
      if (course.exam_date === null) {
        continue;
      }
      let day = jdateToInt(course.exam_date);
      dayToCourse[day] = dayToCourse[day] || [];
      dayToCourse[day].push(course);

      minDay = Math.min(minDay, day);
      maxDay = Math.max(maxDay, day);
    }
    return { minDay, maxDay, dayToCourse };
  }, [courses]);

  const colCount = maxDay - minDay + 1;
  const getCourses = (cellIndex) => {
    const colNumber = cellIndex % colCount;
    const day = maxDay - colNumber;
    if (day in dayToCourse) {
      return dayToCourse[day];
    }
    return [];
  };

  if (colCount <= 0) {
    return null;
  }

  return (
    <>
      <Typography variant="h6" gutterBottom align="center">
        برنامه امتحانی
      </Typography>
      <Box
        sx={{
          display: "grid",
          gridTemplateRows: "auto 1fr",
          gridTemplateColumns: `repeat(${colCount}, 1fr)`,
          border: "1px solid #ddd",
          m: "1%",
          flex: 1,
          minHeight: 0,
        }}
      >
        {Array.from({ length: colCount }).map((_, i) => (
          <Box
            key={i}
            sx={{
              borderRight: "1px solid #eee",
              borderBottom: "1px solid #eee",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              fontSize: 12,
            }}
          >
            <Typography variant="body2" gutterBottom align="center">
              {intToJdate(maxDay - i)}
            </Typography>
          </Box>
        ))}

        {Array.from({ length: colCount }).map((_, i) => {
          const coursesInCell = getCourses(i);
          const clamp = coursesInCell.length > 1 ? 2 : 5;

          return (
            <Box
              key={i}
              sx={{
                borderRight: "1px solid #eee",
                borderBottom: "1px solid #eee",
                display: "flex",
                flexDirection: "column",
                alignItems: "stretch",
                overflow: "hidden",
              }}
            >
              {coursesInCell.map((course) => (
                <ScheduleTableCell
                  key={course.id}
                  course={course}
                  toggleCourse={null}
                  state="selected"
                  variant1="caption"
                  variant2="overline"
                  styleOverrides={{
                    m: "1%",
                    flex: 1,
                    minHeight: 0,
                    clamp: clamp,
                  }}
                />
              ))}
            </Box>
          );
        })}
      </Box>
    </>
  );
}

export default ExamSchedule;
