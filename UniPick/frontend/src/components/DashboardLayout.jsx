import { Box, useMediaQuery, useTheme } from "@mui/material";
import { DashboardLeftWidth, DashboardRightWidth } from "../configs/sizes";

function DashboardLayout({ left, right }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  if (!isMobile) {
    return (
      <Box
        sx={{
          display: "flex",
          flexDirection: "row",
          flex: 1,
          minHeight: 0,
          gap: 1,
        }}
      >
        <Box
          sx={{
            flexBasis: DashboardLeftWidth,
            flexShrink: 0,
            minWidth: 0,
            flexDirection: "column",
            display: "flex",
          }}
        >
          {left}
        </Box>
        <Box
          sx={{
            flexBasis: DashboardRightWidth,
            flexShrink: 0,
            minWidth: 0,
            flexDirection: "column",
            display: "flex",
            minHeight: 0,
          }}
        >
          {right}
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", flex: 1, minHeight: 0, gap: 1 }}>
      {/* Schedule first (left) */}
      <Box sx={{ flex: 2, minHeight: 0, overflow: "auto", "-webkit-overflow-scrolling": "touch" }}>
        {left}
      </Box>
      {/* Course selector below (right) */}
      <Box sx={{ flex: 1, minHeight: 0, overflow: "auto", "-webkit-overflow-scrolling": "touch" }}>
        {right}
      </Box>
    </Box>
  );
}

export default DashboardLayout;