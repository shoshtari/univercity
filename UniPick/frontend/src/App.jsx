import { Box } from "@mui/material";
import { useEffect, useState } from "react";
import CourseSelector from "./components/CourseSelector";
import DashboardLayout from "./components/DashboardLayout";
import { useSnackbar } from "notistack";
import Login from "./components/Login";
import SchedulePanel from "./components/SchedulePanel";
import SemesterInformation from "./components/SemesterInformation/SemesterInformation";
import TopBar from "./components/TopBar";
import { useAuth } from "./hooks/useAuth";
import { useSchedule } from "./hooks/useSchedule";
import { BASE_URL } from "./configs/api";

function App({ darkMode, setDarkMode }) {
  // possible values are 'login', 'schedule'
  // const [viewState, setViewState] = useState("schedule");
  const [viewState, setViewState] = useState("exam");
  const auth = useAuth(setViewState);
  const { enqueueSnackbar } = useSnackbar();

  const [courses, setCourses] = useState([]);
  const schedule = useSchedule(auth.accessKey, courses);

  useEffect(() => {
    schedule.syncUserCoursesWithBackend();
  }, [auth.accessKey, courses]);

  useEffect(() => {
    if (!auth.isAuthenticated) {
      return;
    }
    let cancelled = false;

    (async () => {
      const result = await schedule.getCourses();
      if (!result.ok) {
        enqueueSnackbar("Failed to fetch courses: " + result.error.message, {
          variant: "error",
        });
        return;
      }
      if (!cancelled) {
        setCourses(result.data);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [enqueueSnackbar, auth.isAuthenticated, auth.accessKey]);

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

  async function toggleCourse(course) {
    const result = await schedule.toggleCourse(course);
    if (!result.ok) {
      enqueueSnackbar(`failed to toggle course ${course.name}`, {
        variant: "error",
      });
    }
  }

  if (!auth.isAuthenticated && viewState != "login") {
    return (
      <Login
        doLogin={doLogin}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
        enqueueSnackbar={enqueueSnackbar}
      />
    );
  }

  switch (viewState) {
    case "schedule":
      return (
        <Box sx={{ height: "100vh", display: "flex", flexDirection: "column" }}>
          <TopBar
            user={auth.user}
            darkMode={darkMode}
            setDarkMode={setDarkMode}
            doLogout={auth.logout}
            setViewState={setViewState}
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
                  onSelect={toggleCourse}
                  selectedCourses={schedule.selectedCourses}
                  setPendingCourse={schedule.setPendingCourse}
                />
              }
              left={
                <SchedulePanel
                  courses={schedule.selectedCourses}
                  pendingCourse={schedule.pendingCourse}
                  toggleCourse={toggleCourse}
                />
              }
            />
          </Box>
        </Box>
      );
    case "exam":
      return (
        <Box sx={{ height: "100vh", display: "flex", flexDirection: "column" }}>
          <TopBar
            user={auth.user}
            darkMode={darkMode}
            setDarkMode={setDarkMode}
            doLogout={auth.logout}
            setViewState={setViewState}
          />

              <SemesterInformation
                courses={schedule.selectedCourses}
                pendingCourse={schedule.pendingCourse}
                toggleCourse={toggleCourse}
              />
          </Box>
      );

    default:
      throw new Error("unknown view state " + viewState);
  }
}

export default App;
