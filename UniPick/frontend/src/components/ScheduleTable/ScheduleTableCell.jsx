import { Box, Typography } from "@mui/material";
import { getOpacity } from "./helpers";

function ScheduleTableCell({
  course,
  toggleCourse,
  state,
  variant1 = "body1",
  variant2 = "body2",
  styleOverrides = {},
  isMobile = false,
  clamp = 2,
}) {
  const sx = {
    p: 1,
    backgroundColor: "secondary.main",
    borderRadius: 1,
    minHeight: isMobile ? 48 : "auto",

    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    overflow: "hidden",

    transition: "opacity 0.15s ease, box-shadow 0.15s ease",
    opacity: getOpacity(state),

    ...styleOverrides,
  };

  const handleClick = () => {
    if (toggleCourse != null) {
      toggleCourse(course);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleClick();
    }
  };

  return (
    <Box
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      sx={sx}
    >
      <Typography
        variant={variant1}
        fontWeight={600}
        sx={{
          lineHeight: 1.2,
          direction: "rtl",
          color: "text.primary",

          display: "-webkit-box",
          "-webkit-line-clamp": clamp,
          "-webkit-box-orient": "vertical",
          overflow: "hidden",
        }}
        align="center"
      >
        {course.name}
      </Typography>

      <Typography
        variant={variant2}
        noWrap
        sx={{ lineHeight: 1.2, color: "text.secondary", direction: "rtl" }}
        align="center"
      >
        {course.instructor || "—"}
      </Typography>
    </Box>
  );
}

export default ScheduleTableCell;
