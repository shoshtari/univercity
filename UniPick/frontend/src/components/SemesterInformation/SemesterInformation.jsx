import { Box, Card, CardContent, Typography } from "@mui/material";
import ScheduleTableCell from "../ScheduleTable/ScheduleTableCell";
import { ExamTableRowHeight } from "../../configs/sizes";
import ExamSchedule from "./ExamSchedule";
import CourseTable from "./CourseTable";

function SemesterInformation({ courses }) {
  return (
    <Card sx={{ m: 2, ml: 0, flex: 1, height: "100%" }}>
      <CardContent sx={{ height: "100%" }}>
        <ExamSchedule courses={courses} height="30%" />
        <CourseTable courses={courses} width="30%" />
      </CardContent>
    </Card>
  );
}

export default SemesterInformation;
