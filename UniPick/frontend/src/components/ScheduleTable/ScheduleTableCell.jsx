import { Box, Typography } from "@mui/material";

function ScheduleTableCell({ course, toggleCourse, styleOverrides }) {
  toggleCourse == null ? {} : {};
  let sx = {
    p: 1,
    backgroundColor: "secondary.main",
    borderRadius: 1,

    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    overflow: "hidden",

    transition: "opacity 0.15s ease, box-shadow 0.15s ease",
  };
  sx = {
    ...sx,
    ...styleOverrides,
  };

  return (
    <Box
      onClick={() => {
        if (toggleCourse != null) {
          toggleCourse(course);
        }
      }}
      sx={sx}
    >
      <Typography
        variant={sx.variant1}
        fontWeight={600}
        sx={{
          lineHeight: 1.2,
          direction: "rtl",
          color: "text.primary",

          // the next 4 lines are for 2 line text overflow
          display: "-webkit-box",
          WebkitLineClamp: sx.clamp,
          WebkitBoxOrient: "vertical",
          overflow: "hidden",
        }}
        align="center"
      >
        {course.name}
      </Typography>

      <Typography
        variant={sx.variant2}
        noWrap
        sx={{ lineHeight: 1.2, color: "text.secondary", direction: "rtl" }}
        align="center"
      >
        {course.instructor}
      </Typography>
    </Box>
  );
}

export default ScheduleTableCell;
