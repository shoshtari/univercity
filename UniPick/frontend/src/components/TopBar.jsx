import { AppBar, Box, Toolbar, Typography, IconButton, Menu, MenuItem, Link } from "@mui/material";
import { useCallback, useState } from "react";
import ThemeIcon from "./ThemeIcon";
import { VIEW } from "../configs/views";
import LogoutIcon from "@mui/icons-material/Logout";
import MenuIcon from "@mui/icons-material/Menu";
import { useMediaQuery, useTheme } from "@mui/material";

function TopBar({ user, doLogout, darkMode, setDarkMode, setViewState }) {
  const [anchorEl, setAnchorEl] = useState(null);
  const muiTheme = useTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down("md"));

  const scheduleOnClick = useCallback(() => {
    setViewState(VIEW.SCHEDULE);
    setAnchorEl(null);
  }, [setViewState]);

  const examOnClick = useCallback(() => {
    setViewState(VIEW.EXAM);
    setAnchorEl(null);
  }, [setViewState]);

  const handleMenuOpen = useCallback((event) => {
    setAnchorEl(event.currentTarget);
  }, []);

  const linkStyles = {
    color: "white",
    textDecoration: "underline",
    textUnderlineOffset: "6px",
    fontWeight: "bold",
    fontSize: "1rem",
    textDecorationThickness: "2px",
    mx: "0.5%",
    cursor: "pointer",
  };

  const linkDisplay = { xs: "hidden", sm: "hidden", md: "flex" };
  const menuButtonTheme = { xs: "flex", sm: "flex", md: "none" };

  return (
    <AppBar position="static" elevation={2} sx={{ minHeight: isMobile ? 56 : 64 }}>
      <Toolbar
        sx={{
          px: { xs: 1, sm: 2 },
          minHeight: isMobile ? 56 : 64,
        }}
        disableGutters={isMobile}
      >
        <IconButton
          onClick={doLogout}
          sx={{
            transition: "transform 0.3s ease",
            "&:hover": {
              transform: "rotate(-20deg)",
            },
            display: menuButtonTheme,
            minWidth: 44,
            minHeight: 44,
          }}
          edge="start"
          aria-label="logout"
          size={isMobile ? "small" : "medium"}
        >
          <LogoutIcon fontSize={isMobile ? "medium" : "large"} />
        </IconButton>
        
        <ThemeIcon darkMode={darkMode} setDarkMode={setDarkMode} sx={{ mr: 1 }} />
        
        <Typography 
          variant={isMobile ? "body2" : "body1"} 
          sx={{ mr: 2, display: { xs: "none", sm: "block" }, whiteSpace: "nowrap" }}
        >
          {user} خوش آمدید
        </Typography>
        
        <Box sx={{ flexGrow: 1 }} />
        
        <Box sx={{ display: linkDisplay }}>
          <Link onClick={examOnClick} sx={linkStyles}> وضعیت ترم </Link>
          <Link onClick={scheduleOnClick} sx={linkStyles}> برنامه هفتگی </Link>
        </Box>
        
        <IconButton
          onClick={handleMenuOpen}
          sx={{
            ...menuButtonTheme,
            minWidth: 44,
            minHeight: 44,
          }}
          edge="end"
          aria-label="menu"
          size={isMobile ? "small" : "medium"}
        >
          <MenuIcon fontSize={isMobile ? "medium" : "large"} />
        </IconButton>
        
        <Typography 
          variant={isMobile ? "h6" : "h5"} 
          sx={{ 
            display: { xs: "block", md: "none" }, 
            ml: 1,
            fontSize: { xs: 20, sm: 22 },
          }}
        >
          🎓 UniPick
        </Typography>
        
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
          transformOrigin={{ horizontal: "right", vertical: "top" }}
          anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
          sx={{
            "& .MuiMenuItem-root": {
              py: 1.5,
              fontSize: isMobile ? 16 : 14,
              minHeight: isMobile ? 48 : 44,
            },
          }}
        >
          <MenuItem onClick={scheduleOnClick}>برنامه هفتگی</MenuItem>
          <MenuItem onClick={examOnClick}>وضعیت ترم</MenuItem>
          <MenuItem onClick={doLogout}>خروج</MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
}

export default TopBar;