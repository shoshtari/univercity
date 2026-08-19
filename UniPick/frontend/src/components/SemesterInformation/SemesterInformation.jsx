import { Box, Card, CardContent, Typography } from "@mui/material";
import ScheduleTableCell from "../ScheduleTable/ScheduleTableCell";
import ExamSchedule from "./ExamSchedule";
import CourseTable from "./CourseTable";

function SemesterInformation({ courses }) {
  return (
    <Card sx={{ m: 2, ml: 0, flex: 1, display: "flex", flexDirection: "column" }}>
      <CardContent sx={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <ExamSchedule courses={courses} />
        <CourseTable courses={courses} />
      </CardContent>
    </Card>
  );
}

export default SemesterInformation;
