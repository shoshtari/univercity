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

function CourseSelector({ courses, selectedCourses,setPendingCourse, onSelect }) {
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
        <Typography variant="h6" gutterBottom align="right">
          دروس
        </Typography>

        <TextField
          fullWidth
          placeholder="جستجو در میان دروس..."
          align="right"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          sx={{
            mb: 2,
            "& input": {
              textAlign: "right",
              direction: "rtl",
            },
          }}
        />

        <List>
          {filtered.map((course) => {
            const color = selectedCourses.some((i) => i.id === course.id)
              ? "action.selected"
              : "transparent";

            let secondRow = "";
            if (course.instructor != null) {
              secondRow += course.instructor + " - ";
            }
            secondRow += "گروه " + course.group;

            return (
              <ListItemButton
                key={course.id}
                onClick={() => onSelect(course)}
				onMouseEnter={() => (setPendingCourse(course))}
				onMouseLeave={() => (setPendingCourse(null))}
                sx={{ backgroundColor: color }}
              >
                <ListItemText
                  align="right"
                  primary={`${course.name} - ${course.code}`}
                  secondary={`${secondRow}`}
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
