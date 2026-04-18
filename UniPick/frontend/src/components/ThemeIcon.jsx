import { IconButton } from "@mui/material";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import LightModeIcon from "@mui/icons-material/LightMode";

function ThemeIcon({ darkMode, setDarkMode }) {
  return (
    <IconButton  onClick={() => {setDarkMode(!darkMode)}}>
      {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
    </IconButton>
  );
}

export default ThemeIcon;
