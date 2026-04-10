import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import ScheduleTableCell from "./ScheduleTableCell";
import {
  ScheduleTableFirstColWidth,
  ScheduleTableOtherColWidth,
  ScheduleTableRowHeight,
} from "../configs/sizes";

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"];
const HOURS = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17];

function ScheduleTable({ courses }) {
  function getCourseForSlot(day, hour) {
    return courses.find(
      (course) =>
        course.days.includes(day) &&
        hour >= course.startHour &&
        hour < course.endHour,
    );
  }

  return (
    <TableContainer component={Paper} sx={{ overflowX: "auto" }}>
      <Table sx={{ tableLayout: "fixed" }}>
        <colgroup>
          <col style={{ width: ScheduleTableFirstColWidth }} />
          {HOURS.map((_, i) => (
            <col key={i} style={{ width: ScheduleTableOtherColWidth }} />
          ))}
        </colgroup>

        <TableHead>
          <TableRow sx={{ height: ScheduleTableRowHeight }}>
            <TableCell align="center">
              <strong>Day / Time</strong>
            </TableCell>
            {HOURS.map((hour) => (
              <TableCell key={hour} align="center">
                {hour}:00
              </TableCell>
            ))}
          </TableRow>
        </TableHead>

        <TableBody>
          {DAYS.map((day) => (
            <TableRow key={day} sx={{ height: ScheduleTableRowHeight }}>
              <TableCell align="center">
                <strong>{day}</strong>
              </TableCell>

              {HOURS.map((hour) => {
                const course = getCourseForSlot(day, hour);
                return <ScheduleTableCell key={hour} course={course} />;
              })}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default ScheduleTable;
