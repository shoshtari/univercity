import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
} from "@mui/material";
import { useMediaQuery, useTheme } from "@mui/material";

import { useState } from "react";
import { LoginCardWidth } from "../configs/sizes";
import ThemeIcon from "./ThemeIcon";
import { signup } from "../api/auth";

function Login({ doLogin, darkMode, setDarkMode, enqueueSnackbar }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  async function handleSubmit(e) {
    e.preventDefault();
    if (!username.trim() || !password) {
      enqueueSnackbar("Username and password cannot be empty", {
        variant: "warning",
      });
      return;
    }

    switch (e.nativeEvent.submitter.name) {
      case "signup": {
        const result = await signup(username, password);
        if (result.ok) {
          enqueueSnackbar("Signup successful! You can now log in.", {
            variant: "success",
          });
          await doLogin(username, password);
        } else {
          enqueueSnackbar(result.error.message, {
            variant: "error",
          });
        }

        break;
      }
      case "login":
        await doLogin(username, password);
        break;
      default:
        alert("unknown action");
    }
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        p: { xs: 1.5, sm: 2, md: 3 },
        boxSizing: "border-box",
      }}
    >
      <Card sx={{ width: LoginCardWidth, maxWidth: "100%", p: { xs: 2, sm: 3 } }}>
        <CardContent>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 2,
            }}
          >
            <Typography variant={isMobile ? "h6" : "h5"} sx={{ mb: 0 }}>UniPick</Typography>
            <ThemeIcon darkMode={darkMode} setDarkMode={setDarkMode} />
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Sign in to continue
          </Typography>

          <form onSubmit={handleSubmit}>
            <TextField
              label="Username"
              fullWidth
              margin="normal"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              sx={{ mb: 2 }}
              size={isMobile ? "small" : "medium"}
              InputProps={{
                inputProps: { autoComplete: "username" },
              }}
            />
            <TextField
              label="Password"
              fullWidth
              type="password"
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              sx={{ mb: 2 }}
              size={isMobile ? "small" : "medium"}
              InputProps={{
                inputProps: { autoComplete: "current-password" },
              }}
            />

            <Box sx={{ display: "flex", flexDirection: { xs: "column", sm: "row" }, gap: 2 }}>
              <Button
                type="submit"
                variant="contained"
                name="signup"
                size={isMobile ? "large" : "medium"}
                sx={{ mt: { xs: 0, sm: 2 }, flex: 1, width: "100%", minHeight: isMobile ? 48 : "auto" }}
              >
                Sign up
              </Button>
              <Button
                type="submit"
                variant="contained"
                name="login"
                size={isMobile ? "large" : "medium"}
                sx={{ mt: { xs: 0, sm: 2 }, flex: 1, width: "100%", minHeight: isMobile ? 48 : "auto" }}
              >
                Login
              </Button>
            </Box>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}

export default Login;