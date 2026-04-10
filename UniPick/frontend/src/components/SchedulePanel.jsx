import { Card, CardContent, Typography } from "@mui/material";
import ScheduleTable from "./ScheduleTable";

function SchedulePanel({ courses }) {
  return (
    <Card sx={{ m: 2, ml: 0, flex: 1 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Weekly Schedule
        </Typography>

        <ScheduleTable courses={courses} />
      </CardContent>
    </Card>
  );
}

export default SchedulePanel;
