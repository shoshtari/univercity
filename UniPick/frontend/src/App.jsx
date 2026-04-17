import { Box } from "@mui/material";
import { useEffect, useState } from "react";
import getCourses from "./api/courses";
import CourseSelector from "./components/CourseSelector";
import DashboardLayout from "./components/DashboardLayout";
import { useSnackbar } from "notistack";
import Login from "./components/Login";
import SchedulePanel from "./components/SchedulePanel";
import TopBar from "./components/TopBar";
import { useAuth } from "./hooks/useAuth";
import { useSchedule } from "./hooks/useSchedule";

function App({ darkMode, setDarkMode }) {
  const auth = useAuth();
	const schedule = useSchedule();
  const { enqueueSnackbar } = useSnackbar();

  const [courses, setCourses] = useState([]);

  useEffect(() => {
    if (!auth.isAuthenticated) {
      return;
    }
    let cancelled = false;

    (async () => {
      const data = await getCourses(auth.accessKey);
      if (!data.ok) {
        enqueueSnackbar("Failed to fetch courses: " + data.error.message, {
          variant: "error",
        });
        return;
      }
      if (!cancelled) {
        setCourses(data.data);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [enqueueSnackbar, auth.isAuthenticated]);

  async function doLogin(username, password) {
    const result = await auth.login(username, password);
    if (result.ok) {
      enqueueSnackbar("Login successful!", { variant: "success" });
    } else {
      enqueueSnackbar("Login failed: " + result.error.message, {
        variant: "error",
      });
    }
  }


  if (!auth.isAuthenticated) {
    return (
      <Login
        doLogin={doLogin}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
        enqueueSnackbar={enqueueSnackbar}
      />
    );
  }

  return (
    <Box sx={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <TopBar
        user={auth.user}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
        doLogout={auth.logout}
      />

      <Box
        sx={{
          flex: 1, // ✅ take remaining height
          minHeight: 0, // ✅ allow children to stretch/scroll
          display: "flex",
        }}
      >
        <DashboardLayout
          right={
            <CourseSelector
              courses={courses}
              onSelect={schedule.toggleCourse}
              selectedCourses={schedule.selectedCourses}
              setPendingCourse={schedule.setPendingCourse}
            />
          }
          left={
            <SchedulePanel
              courses={schedule.selectedCourses}
              pendingCourse={schedule.pendingCourse}
              toggleCourse={schedule.toggleCourse}
            />
          }
        />
      </Box>
    </Box>
  );
}

export default App;
