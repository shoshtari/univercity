import { useCallback, useEffect, useState } from "react";
import { login as apiLogin, getMe } from "../api/auth";


export function useSchedule() {
  const [selectedCourses, setSelectedCourses] = useState([]);
  const [pendingCourse, setPendingCourse] = useState(null);

  function toggleCourse(course) {
    setSelectedCourses((prev) =>
      prev.some((i) => i.code === course.code)
        ? prev.filter((c) => c.code !== course.code)
        : [...prev, course],
    );
  }

  return {
	  selectedCourses,

	  pendingCourse,
	  setPendingCourse,

	  toggleCourse,
  };
}
