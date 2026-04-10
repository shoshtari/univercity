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

function Login({ onLogin, darkMode, setDarkMode }) {
  const [username, setUsername] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (username.trim()) {
      onLogin(username);
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

            <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }}>
              Login
            </Button>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}

export default Login;
