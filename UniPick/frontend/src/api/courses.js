import { MOCK_APIS } from "../configs/api";
import { request } from "./client";
import { ApiResultOk, ApiResultErr } from "./result";

const MOCK_COURSES = [
  {
    id: "1",
    name: "Algorithms",
    code: "CS301",
    instructor: "Dr. Ahmad",
    group: "01",
    courseTimes: [
      { weekday: "Tuesday", start: "10:00:00", end: "11:30:00" },
      { weekday: "Thursday", start: "10:00:00", end: "11:30:00" },
    ],
    units: 1,
    examData: "1405-04-14",
  },
  {
    id: "2",
    name: "Databases",
    code: "CS401",
    instructor: "Dr. Reza",
    group: "01",
    courseTimes: [
      { weekday: "Monday", start: "09:00:00", end: "10:30:00" },
      { weekday: "Wednesday", start: "09:00:00", end: "10:30:00" },
    ],
    units: 2,
    examData: "1405-04-14",
  },
  {
    id: "3",
    name: "Operating Systems",
    code: "CS501",
    instructor: "Dr. Ali",
    group: "01",
    courseTimes: [
      { weekday: "Monday", start: "11:00:00", end: "12:30:00" },
      { weekday: "Wednesday", start: "11:00:00", end: "12:30:00" },
    ],
    units: 1,
    examData: "1405-04-14",
  },
];

export async function getCourses(accessToken) {
  if (MOCK_APIS) {
    await new Promise((r) => setTimeout(r, 300));
    const courses = MOCK_COURSES.map((c) => {
      return c;
    });
    return new ApiResultOk(courses);
  }

  try {
    const result = await request({
      path: "/courses/all",
      options: {
        method: "GET",
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      },
    });

    return new ApiResultOk(result.courses);
  } catch (err) {
    return new ApiResultErr(err);
  }
}

export async function toggleCourse({ accessToken, course_id, change }) {
  if (MOCK_APIS) {
    await new Promise((r) => setTimeout(r, 300));
    return new ApiResultOk(null);
  }

  try {
    await request({
      path: `/courses/${course_id}`,
      options: {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          change: change,
        }),
      },
      parse_response: false,
    });

    return new ApiResultOk(null);
  } catch (err) {
    return new ApiResultErr(err);
  }
}

export async function getUserCourses(accessToken) {
  if (MOCK_APIS) {
    await new Promise((r) => setTimeout(r, 300));
    return new ApiResultOk([]);
  }

  try {
    const result = await request({
      path: "/courses/my",
      options: {
        method: "GET",
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      },
    });

    return new ApiResultOk(result.course_ids);
  } catch (err) {
    return new ApiResultErr(err);
  }
}
