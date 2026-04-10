import DarkModeIcon from "@mui/icons-material/DarkMode";
import LightModeIcon from "@mui/icons-material/LightMode";
import { IconButton } from "@mui/material";

function ThemeIcon({ darkMode, setDarkMode }) {
  return (
    <IconButton
      onClick={() => setDarkMode(!darkMode)}
      sx={{
        transition: "transform 0.3s ease",
        "&:hover": {
          transform: "rotate(20deg)",
        },
      }}
    >
      {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
    </IconButton>
  );
}

export default ThemeIcon;
