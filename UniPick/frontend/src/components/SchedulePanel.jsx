import { Card, CardContent, Typography } from "@mui/material";
import ScheduleTable from "./ScheduleTable/ScheduleTable";

function SchedulePanel({ courses, pendingCourse, toggleCourse }) {

  return (
    <Card sx={{ m: { xs: 1, sm: 2 }, flex: 1, minHeight: 0 }}>
      <CardContent sx={{ flex: 1, minHeight: 0, p: { xs: 1, sm: 2 } }}>
        <Typography variant="h6" gutterBottom align="center" sx={{ mb: 2 }}>
          برنامه هفتگی
        </Typography>

        <ScheduleTable courses={courses} pendingCourse={pendingCourse} toggleCourse={toggleCourse} />
      </CardContent>
    </Card>
  );
}

export default SchedulePanel;
