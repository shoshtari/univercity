import { useState, useCallback } from "react";
import {
  getCourses as getCoursesApi,
  toggleCourse as toggleCourseApi,
  getUserCourses,
} from "../api/courses";

export function useSchedule(accessToken, courses) {
  const [selectedCourses, setSelectedCourses] = useState([]);
  const [pendingCourse, setPendingCourse] = useState(null);

  const syncUserCoursesWithBackend = useCallback(async () => {
    if (accessToken === null || courses.length === 0) {
      return;
    }
    const result = await getUserCourses(accessToken);
    if (!result.ok) {
      return false;
    }

    const userCourses = [];
    for (const course_id of result.data) {
      const course = courses.find((i) => i.id === course_id);
      if (course != null) {
        userCourses.push(course);
      }
    }
    setSelectedCourses(userCourses);
  }, [accessToken, courses]);

  const toggleCourse = useCallback(
    async (course) => {
      let setChange;
      const change = new Promise((resolve) => {
        setChange = resolve;
      });

      const toggleFunc = (prev) => {
        if (prev.some((i) => i.id === course.id)) {
          setChange("remove");
          return prev.filter((c) => c.id !== course.id);
        }
        setChange("add");
        return [...prev, course];
      };

      setSelectedCourses(toggleFunc);

      const result = await toggleCourseApi({
        course_id: course.id,
        accessToken: accessToken,
        change: await change,
      });
      if (!result.ok) {
        setSelectedCourses(toggleFunc); // rollback
      }
      return result;
    },
    [accessToken],
  );

  const getCourses = useCallback(() => {
    return getCoursesApi(accessToken);
  }, [accessToken]);

  return {
    selectedCourses,

    pendingCourse,
    setPendingCourse,

    toggleCourse,
    getCourses,

    syncUserCoursesWithBackend,
  };
}
