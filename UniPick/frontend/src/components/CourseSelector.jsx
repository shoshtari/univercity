import {
  Card,
  CardContent,
  List,
  ListItemButton,
  ListItemText,
  TextField,
  Typography,
} from "@mui/material";

import { useMemo, useState } from "react";

function CourseSelector({ courses, selectedCourses, onSelect }) {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    return courses.filter(
      (course) =>
        course.name.toLowerCase().includes(query.toLowerCase()) ||
        course.code.toLowerCase().includes(query.toLowerCase()),
    );
  }, [courses, query]);

  return (
    <Card
      sx={{
        m: 2,
        display: "flex",
        flex: 1,
        minHeight: 0,
        flexDirection: "column",
      }}
    >
      <CardContent sx={{ flex: 1, minHeight: 0, overflow: "auto" }}>
        <Typography variant="h6" gutterBottom>
          Courses
        </Typography>

        <TextField
          fullWidth
          placeholder="Search course..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          sx={{ mb: 2 }}
        />

        <List>
          {filtered.map((course) => {
            const color = selectedCourses.some((i) => i.code === course.code)
              ? "action.selected"
              : "transparent";

            return (
              <ListItemButton
                key={course.code}
                onClick={() => onSelect(course)}
                sx={{ backgroundColor: color }}
              >
                <ListItemText
                  primary={`${course.code} – ${course.name}`}
                  secondary={course.days.join(", ") + " @ " + course.startHour}
                />
              </ListItemButton>
            );
          })}
        </List>
      </CardContent>
    </Card>
  );
}

export default CourseSelector;
