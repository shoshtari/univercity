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
        } else {
          enqueueSnackbar(result.error.message, {
            variant: "error",
          });
        }
        await doLogin(username, password);

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
      }}
    >
      <Card sx={{ width: LoginCardWidth }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between">
            <Typography variant="h5">UniPick</Typography>
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
            />
            <TextField
              label="Password"
              fullWidth
              type="password"
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            <Button
              type="submit"
              variant="contained"
              name="signup"
              sx={{ mt: 2, mr: 1, width: "46%" }}
            >
              Sign up
            </Button>
            <Button
              type="submit"
              variant="contained"
              name="login"
              sx={{ mt: 2, ml: 1, width: "46%" }}
            >
              Login
            </Button>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}

export default Login;
