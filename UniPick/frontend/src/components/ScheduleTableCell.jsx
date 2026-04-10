import { TableCell, Typography } from "@mui/material";

function ScheduleTableCell({ course }) {
  return (
    <TableCell align="center">
      <Typography
        sx={{
          textOverflow: "ellipsis",
          overflow: "hidden",
          whiteSpace: "nowrap",
        }}
        variant="body2"
        color="textPrimary"
      >
        {course ? course.name : ""}
      </Typography>

      <Typography variant="body2" color="textSecondary">
        {course ? course.code : ""}
      </Typography>
    </TableCell>
  );
}

export default ScheduleTableCell;
