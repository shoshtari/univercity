import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

import CssBaseline from "@mui/material/CssBaseline";
	  import { SnackbarProvider } from "notistack";
import { ThemeProvider } from "@mui/material/styles";
import { darkTheme, lightTheme } from "./theme";

// eslint-disable-next-line react-refresh/only-export-components
function Root() {
  const [darkMode, setDarkMode] = React.useState(() => {
    const saved = localStorage.getItem("darkMode");
    return saved ? JSON.parse(saved) : false;
  });

  React.useEffect(() => {
    localStorage.setItem("darkMode", JSON.stringify(darkMode));
  }, [darkMode]);

  return (
    <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
      <CssBaseline />
	<SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: "top", horizontal: "center" }}>
      <App darkMode={darkMode} setDarkMode={setDarkMode} />
	  </SnackbarProvider>
    </ThemeProvider>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<Root />);
