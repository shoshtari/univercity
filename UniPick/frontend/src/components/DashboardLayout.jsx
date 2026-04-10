import { Box } from "@mui/material";
import { DashboardLeftWidth, DashboardRightWidth } from "../configs/sizes";

function DashboardLayout({ left, right }) {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "row",
        flex: 1,
        minHeight: 0,
      }}
    >
      <Box
        sx={{
          width: DashboardLeftWidth,
          minWidth: 0,
          flexDirection: "column",
          display: "flex",
        }}
      >
        {left}
      </Box>
      <Box
        sx={{
          width: DashboardRightWidth,
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

export default DashboardLayout;
