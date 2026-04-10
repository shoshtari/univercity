const MOCK_COURSES = [
  {
    name: "Algorithms",
    code: "CS301",
    days: ["Mon", "Wed"],
    startHour: 10,
    endHour: 11.5,
  },
  {
    name: "Databases",
    code: "CS305",
    days: ["Tue", "Thu"],
    startHour: 9,
    endHour: 10.5,
  },
  {
    name: "Operating Systems",
    code: "CS401",
    days: ["Mon", "Wed"],
    startHour: 11,
    endHour: 12.5,
  },
];
async function getCourses() {
  await new Promise((r) => setTimeout(r, 300));
  return MOCK_COURSES.map((c) => {
    return c;
  }); // TODO: this is mocked, implement the api call
}
export default getCourses;
