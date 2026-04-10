import { AppBar, Box, Toolbar, Typography } from "@mui/material";

import ThemeIcon from "./ThemeIcon";

function TopBar({ user, darkMode, setDarkMode }) {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6">🎓 UniPick</Typography>

        <Box sx={{ flexGrow: 1 }} />

        <Typography sx={{ mr: 2 }}>Welcome, {user}</Typography>

        <ThemeIcon darkMode={darkMode} setDarkMode={setDarkMode} />
      </Toolbar>
    </AppBar>
  );
}

export default TopBar;
