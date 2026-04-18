import { AppBar, Box, Toolbar, Typography } from "@mui/material";

import { IconButton } from "@mui/material";
import ThemeIcon from "./ThemeIcon";

import LogoutIcon from "@mui/icons-material/Logout";

function TopBar({ user, doLogout, darkMode, setDarkMode }) {
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
        <Box sx={{ flexGrow: 1 }} />
        <Typography sx={{ mr: 2 }}>{user} خوش آمدید</Typography>
        <Typography variant="h6">🎓 UniPick</Typography>
      </Toolbar>
    </AppBar>
  );
}

export default TopBar;
