import { Box } from "@mui/material";
import { useEffect, useState } from "react";
import getCourses from "./api/courses";
import CourseSelector from "./components/CourseSelector";
import DashboardLayout from "./components/DashboardLayout";
import Login from "./components/Login";
import SchedulePanel from "./components/SchedulePanel";
import TopBar from "./components/TopBar";

function App({ darkMode, setDarkMode }) {
  const [selectedCourses, setSelectedCourses] = useState([]);

  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("user");
    return saved ? JSON.parse(saved) : null;
  });

  useEffect(() => {
    localStorage.setItem("user", JSON.stringify(user));
  }, [user]);

  const [courses, setCourses] = useState([]);
  useEffect(() => {
    let cancelled = false;

    (async () => {
      const data = await getCourses();
      if (!cancelled) {
        setCourses(data);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  function toggleCourse(course) {
    setSelectedCourses((prev) =>
      prev.some((i) => i.code === course.code)
        ? prev.filter((c) => c.code !== course.code)
        : [...prev, course],
    );
  }

  if (!user) {
    return (
      <Login onLogin={setUser} darkMode={darkMode} setDarkMode={setDarkMode} />
    );
  }

  return (
    <Box sx={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <TopBar user={user} darkMode={darkMode} setDarkMode={setDarkMode} />

      <Box
        sx={{
          flex: 1, // ✅ take remaining height
          minHeight: 0, // ✅ allow children to stretch/scroll
          display: "flex",
        }}
      >
        <DashboardLayout
          left={
            <CourseSelector
              courses={courses}
              onSelect={toggleCourse}
              selectedCourses={selectedCourses}
            />
          }
          right={<SchedulePanel courses={selectedCourses} />}
        />
      </Box>
    </Box>
  );
}

export default App;
