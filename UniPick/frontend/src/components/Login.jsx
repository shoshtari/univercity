import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
} from "@mui/material";

import { useState } from "react";
import { LoginCardWidth } from "../configs/sizes";
import ThemeIcon from "./ThemeIcon";
import { signup } from "../api/auth";

function Login({ doLogin, darkMode, setDarkMode, enqueueSnackbar }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");


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
        p: { xs: 2, sm: 3, md: 4 },
        boxSizing: "border-box",
      }}
    >
      <Card sx={{ width: LoginCardWidth, maxWidth: "100%", p: { xs: 2, sm: 3 } }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h5" sx={{ mb: 0 }}>UniPick</Typography>
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
            />
            <TextField
              label="Password"
              fullWidth
              type="password"
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              sx={{ mb: 2 }}
            />

            <Box sx={{ display: "flex", flexDirection: { xs: "column", sm: "row" }, gap: 2 }}>
              <Button
                type="submit"
                variant="contained"
                name="signup"
                sx={{ mt: { xs: 0, sm: 2 }, flex: 1, width: "100%" }}
              >
                Sign up
              </Button>
              <Button
                type="submit"
                variant="contained"
                name="login"
                sx={{ mt: { xs: 0, sm: 2 }, flex: 1, width: "100%" }}
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