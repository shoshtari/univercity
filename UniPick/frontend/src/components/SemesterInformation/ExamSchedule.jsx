import { Box, Card, CardContent, Typography, useMediaQuery, useTheme } from "@mui/material";
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
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

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

  // Mobile vertical view - list of exam days with courses (matching desktop grid design)
  if (isMobile) {
    const sortedDays = Array.from({ length: colCount }).map((_, i) => maxDay - i);

    return (
      <Box sx={{ width: "100%", overflow: "auto", webkitOverflowScrolling: "touch", px: 1 }}>
        <Typography variant="h6" gutterBottom align="center" sx={{ mb: 2 }}>
          برنامه امتحانی
        </Typography>
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            gap: 1.5,
            pb: 2,
          }}
        >
          {sortedDays.map((day) => {
            const coursesInDay = dayToCourse[day] || [];
            return (
              <Card key={day} sx={{ px: 1, py: 1, width: "100%" }}>
                <Box sx={{ mb: 1, borderBottom: 1, borderColor: "divider", pb: 1 }}>
                  <Typography variant="subtitle1" fontWeight={600} align="center">
                    {intToJdate(day)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" align="center">
                    {coursesInDay.length} امتحان
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                  {coursesInDay.length === 0 ? (
                    <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 2 }}>
                      امتحانی در این روز وجود ندارد
                    </Typography>
                  ) : (
                    coursesInDay.map((course) => (
                      <ScheduleTableCell
                        key={course.id}
                        course={course}
                        toggleCourse={null}
                        state="selected"
                        variant1="body2"
                        variant2="caption"
                        isMobile={isMobile}
                        styleOverrides={{
                          m: "1%",
                          flex: 1,
                          minHeight: 56,
                          clamp: coursesInDay.length > 1 ? 2 : 5,
                        }}
                      />
                    ))
                  )}
                </Box>
              </Card>
            );
          })}
        </Box>
      </Box>
    );
  }

  // Desktop grid view (original)
  return (
    <>
      <Typography variant="h6" gutterBottom align="center" sx={{ mb: 2 }}>
        برنامه امتحانی
      </Typography>
      <Box
        sx={{
          overflowX: "auto",
          width: "100%",
          webkitOverflowScrolling: "touch",
          pb: 2,
        }}
      >
        <Box
          sx={{
            display: "grid",
            gridTemplateRows: `auto 1fr`,
            gridTemplateColumns: `repeat(${colCount}, minmax(120px, 1fr))`,
            border: "1px solid #ddd",
            m: "1%",
            flex: 1,
            minHeight: 0,
            minWidth: "max-content",
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
                whiteSpace: "nowrap",
                py: 1,
                fontWeight: 500,
                color: "text.secondary",
              }}
            >
              <Typography variant="body2" gutterBottom align="center" sx={{ lineHeight: 1.3 }}>
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
                  minHeight: { xs: "70px", sm: "80px", md: "90px", lg: "90px", xl: "90px" },
                }}
              >
                <>
                  {coursesInCell.map((course) => (
                    <ScheduleTableCell
                      key={course.id}
                      course={course}
                      toggleCourse={null}
                      state="selected"
                      variant1="body2"
                      variant2="caption"
                      isMobile={isMobile}
                      styleOverrides={{
                        m: "1%",
                        flex: 1,
                        clamp: clamp,
                      }}
                    />
                  ))}
                  {coursesInCell.length === 0 && (
                    <Box sx={{ flex: 1 }} />
                  )}
                </>
              </Box>
            );
          })}
        </Box>
      </Box>
    </>
  );
}

export default ExamSchedule;