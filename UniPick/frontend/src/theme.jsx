import { createTheme } from "@mui/material/styles";

const baseTheme = {
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          transition: "background-color 0.3s ease, color 0.3s ease",
        },
      },
    },

    MuiPaper: {
      styleOverrides: {
        root: {
          transition: "background-color 0.3s ease, box-shadow 0.3s ease",
        },
      },
    },

    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
          transition: "background-color 0.3s ease, color 0.3s ease",
        },
      },
    },

    MuiTableRow: {
      styleOverrides: {
        root: {
          transition: "background-color 0.2s ease",
        },
      },
    },

    MuiListItemButton: {
      styleOverrides: {
        root: {
          transition: "background-color 0.2s ease",
        },
      },
    },
  },
};

export const lightTheme = createTheme({
  ...baseTheme,
  palette: {
    mode: "light",

    primary: {
      main: "#1976d2",
    },

    background: {
      default: "#f5f7fa",
      paper: "#ffffff",
    },

    text: {
      primary: "#1c1c1c",
      secondary: "#555555",
    },

    divider: "rgba(0, 0, 0, 0.12)",

    action: {
      hover: "rgba(0, 0, 0, 0.04)",
      selected: "rgba(25, 118, 210, 0.12)",
      disabled: "rgba(0, 0, 0, 0.26)",
      disabledBackground: "rgba(0, 0, 0, 0.12)",
    },
  },
});

export const darkTheme = createTheme({
  ...baseTheme,
  palette: {
    mode: "dark",

    primary: {
      main: "#90caf9",
    },

    background: {
      default: "#121212",
      paper: "#1e1e1e",
    },

    text: {
      primary: "#ffffff",
      secondary: "#b0b0b0",
    },

    divider: "rgba(255, 255, 255, 0.12)",

    action: {
      hover: "rgba(255, 255, 255, 0.08)",
      selected: "rgba(144, 202, 249, 0.16)",
      disabled: "rgba(255, 255, 255, 0.3)",
      disabledBackground: "rgba(255, 255, 255, 0.12)",
    },
  },
});
