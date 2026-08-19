import { Box, useMediaQuery, useTheme, Tabs, Tab } from "@mui/material";
import { useState } from "react";
import { DashboardLeftWidth, DashboardRightWidth } from "../configs/sizes";

function DashboardLayout({ left, right }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const [mobileTab, setMobileTab] = useState(0); // 0 = schedule, 1 = courses

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
            width: DashboardLeftWidth,
            minWidth: 0,
            flexDirection: "column",
            display: "flex",
            flex: 3,
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
            flex: 1,
          }}
        >
          {right}
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", flex: 1, minHeight: 0 }}>
      <Tabs
        value={mobileTab}
        onChange={(_, v) => setMobileTab(v)}
        sx={{
          borderBottom: 1,
          borderColor: "divider",
          px: 1,
          minHeight: 48,
          "& .MuiTab-root": {
            minHeight: 48,
            textTransform: "none",
            fontSize: 14,
            fontWeight: 500,
          },
        }}
        variant="fullWidth"
      >
        <Tab label="برنامه هفتگی" />
        <Tab label="دروس" />
      </Tabs>
      <Box sx={{ flex: 1, minHeight: 0, overflow: "hidden" }}>
        {mobileTab === 0 ? left : right}
      </Box>
    </Box>
  );
}

export default DashboardLayout;