import { AppBar, Box, Toolbar, Typography } from "@mui/material";

import { IconButton, Link } from "@mui/material";
import { useCallback } from "react";
import ThemeIcon from "./ThemeIcon";

import LogoutIcon from "@mui/icons-material/Logout";

function TopBar({ user, doLogout, darkMode, setDarkMode, setViewState }) {

  const scheduleOnClick = useCallback(() => {
    setViewState("schedule");
  }, [setViewState]);

  const examOnClick = useCallback(() => {
    setViewState("exam");
  }, [setViewState]);

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

  return (
    <AppBar position="static">
      <Toolbar>
        <IconButton
          onClick={doLogout}
          sx={{
            transition: "transform 0.3s ease",
            "&:hover": {
              transform: "rotate(-20deg)",
            },
          }}
        >
          <LogoutIcon />
        </IconButton>
        <ThemeIcon darkMode={darkMode} setDarkMode={setDarkMode} />
        <Typography sx={{ mr: 2 }}>{user} خوش آمدید</Typography>
        <Box sx={{ flexGrow: 1 }} />
        <Link onClick={examOnClick} sx={linkStyles}> وضعیت ترم </Link>
        <Link onClick={scheduleOnClick} sx={linkStyles}>  برنامه هفتگی </Link>
        <Typography variant="h6">🎓 UniPick</Typography>
      </Toolbar>
    </AppBar>
  );
}

export default TopBar;
