import { Box, Card, CardContent, Typography } from "@mui/material";
import ExamSchedule from "./ExamSchedule";
import CourseTable from "./CourseTable";

function SemesterInformation({ courses }) {
  if (!courses || courses.length === 0) {
    return (
      <Card sx={{ m: { xs: 1, sm: 2 }, flex: 1, display: "flex", flexDirection: "column" }}>
        <CardContent sx={{ flex: 1, display: "flex", flexDirection: "column", p: { xs: 1, sm: 2 }, justifyContent: "center", alignItems: "center" }}>
          <Typography variant="body1" color="text.secondary" align="center">
            درسی برای نمایش وجود ندارد
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box sx={{ flex: 1, display: "flex", flexDirection: "column", m: { xs: 1, sm: 2 }, overflow: "auto", webkitOverflowScrolling: "touch" }}>
      <ExamSchedule courses={courses} />
      <CourseTable courses={courses} />
    </Box>
  );
}

export default SemesterInformation;