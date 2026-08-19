import { AppBar, Box, Toolbar, Typography, IconButton, Menu, MenuItem, Link } from "@mui/material";
import { useCallback, useState, useRef } from "react";
import ThemeIcon from "./ThemeIcon";
import { VIEW } from "../configs/views";
import LogoutIcon from "@mui/icons-material/Logout";
import MenuIcon from "@mui/icons-material/Menu";

function TopBar({ user, doLogout, darkMode, setDarkMode, setViewState }) {
  const [anchorEl, setAnchorEl] = useState(null);
  const menuRef = useRef(null);

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

  const theme = { xs: "hidden", sm: "hidden", md: "flex" };
  const menuButtonTheme = { xs: "flex", sm: "flex", md: "none" };

  return (
    <AppBar position="static" elevation={2}>
      <Toolbar>
        <IconButton
          onClick={doLogout}
          sx={{
            transition: "transform 0.3s ease",
            "&:hover": {
              transform: "rotate(-20deg)",
            },
            display: menuButtonTheme,
          }}
          edge="start"
          aria-label="logout"
        >
          <LogoutIcon />
        </IconButton>
        
        <ThemeIcon darkMode={darkMode} setDarkMode={setDarkMode} />
        
        <Typography sx={{ mr: 2, display: { xs: "none", sm: "block" } }}>
          {user} خوش آمدید
        </Typography>
        
        <Box sx={{ flexGrow: 1 }} />
        
        <Box sx={{ display: theme }}>
          <Link onClick={examOnClick} sx={linkStyles}> وضعیت ترم </Link>
          <Link onClick={scheduleOnClick} sx={linkStyles}> برنامه هفتگی </Link>
        </Box>
        
        <IconButton
          onClick={handleMenuOpen}
          sx={menuButtonTheme}
          edge="end"
          aria-label="menu"
        >
          <MenuIcon />
        </IconButton>
        
        <Typography variant="h6" sx={{ display: { xs: "block", md: "none" }, ml: 1 }}>
          🎓 UniPick
        </Typography>
        
        <Typography variant="h6" sx={{ display: { xs: "none", md: "block" } }}>
          🎓 UniPick
        </Typography>
        
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
          transformOrigin={{ horizontal: "right", vertical: "top" }}
          anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
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