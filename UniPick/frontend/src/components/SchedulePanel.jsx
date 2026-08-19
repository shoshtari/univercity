import { Card, CardContent, Typography } from "@mui/material";
import ScheduleTable from "./ScheduleTable/ScheduleTable";

function SchedulePanel({ courses, pendingCourse, toggleCourse }) {
  return (
    <Card sx={{ m: { xs: 1, sm: 2 }, ml: 0, flex: 1, minHeight: 0 }}>
      <CardContent sx={{ flex: 1, minHeight: 0 }}>
        <Typography variant="h6" gutterBottom align="center">
	  برنامه هفتگی
        </Typography>

        <ScheduleTable courses={courses} pendingCourse={pendingCourse} toggleCourse={toggleCourse} />
      </CardContent>
    </Card>
  );
}

export default SchedulePanel;
