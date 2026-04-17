import { Box, Typography } from "@mui/material";
import { getOpacity, getLeftAndWidth} from "./helpers";

function ScheduleTableCell({ course, toggleCourse, start, end, state }) {
  const { left, width } = getLeftAndWidth(start, end);
  const opacity = getOpacity(state);

  return (
    <Box
      onClick={() => {
        toggleCourse(course);
      }}
      sx={{
        position: "absolute",
        left: `${left}%`,
        width: `${width}%`,
        top: 6,
        bottom: 6,

        backgroundColor: "secondary.main",
        opacity: opacity,
        borderRadius: 1,
        px: 1,

        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        overflow: "hidden",
        cursor: "pointer",

        // ✅ bring hovered item to front & full opacity
        transition: "opacity 0.15s ease, box-shadow 0.15s ease",
        "&:hover": {
          opacity: 1,
          zIndex: 2,
          boxShadow: 3,
        },
      }}
    >
      <Typography
        variant="subtitle1"
        fontWeight={600}
        sx={{
          lineHeight: 1.2,
          direction: "rtl",
          color: "text.primary",

          // the next 4 lines are for 2 line text overflow
          display: "-webkit-box",
          WebkitLineClamp: 2,
          WebkitBoxOrient: "vertical",
          overflow: "hidden",
        }}
        align="center"
      >
        {course.name}
      </Typography>

      <Typography
        variant="subtitle2"
        noWrap
        sx={{ lineHeight: 1.2, color: "text.secondary" }}
        align="center"
      >
        {course.instructor}
      </Typography>
    </Box>
  );
}

export default ScheduleTableCell;
