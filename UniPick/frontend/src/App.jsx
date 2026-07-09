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
import { VIEW } from "./configs/views";

function App({ darkMode, setDarkMode }) {
  const [viewState, setViewState] = useState(VIEW.SCHEDULE);
  const auth = useAuth(setViewState);
  const { enqueueSnackbar } = useSnackbar();

  const [courses, setCourses] = useState([]);
  const schedule = useSchedule(auth.accessKey, courses);
  const { getCourses, syncUserCoursesWithBackend } = schedule;

  useEffect(() => {
    syncUserCoursesWithBackend();
  }, [syncUserCoursesWithBackend]);

  useEffect(() => {
    if (!auth.isAuthenticated) {
      return;
    }
    let cancelled = false;

    (async () => {
      const result = await getCourses();
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
  }, [enqueueSnackbar, getCourses, auth.isAuthenticated]);

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

  if (!auth.isAuthenticated && viewState !== VIEW.LOGIN) {
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
    case VIEW.SCHEDULE:
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
    case VIEW.EXAM:
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
