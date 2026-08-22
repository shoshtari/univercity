import {
  Card,
  CardContent,
  List,
  ListItemButton,
  TextField,
  Typography,
  Chip,
  Box,
} from "@mui/material";
import { useMediaQuery, useTheme } from "@mui/material";

import { useMemo, useState } from "react";

function CourseSelector({ courses, selectedCourses, setPendingCourse, onSelect }) {
  const [query, setQuery] = useState("");
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

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
        m: { xs: 1, sm: 2 },
        display: "flex",
        flex: 1,
        minHeight: 0,
        flexDirection: "column",
      }}
    >
      <CardContent sx={{ flex: 1, minHeight: 0, overflow: "auto", p: { xs: 2, sm: 3 } }}>
        <Typography variant="h6" gutterBottom align="right" sx={{ mb: 2 }}>
          دروس
        </Typography>

        <TextField
          fullWidth
          placeholder="جستجو در میان دروس..."
          align="right"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          size={isMobile ? "small" : "medium"}
          sx={{
            mb: 2,
            "& input": {
              textAlign: "right",
              direction: "rtl",
              fontSize: { xs: 16, sm: 14 },
            },
            "& label": {
              fontSize: { xs: 14, sm: 13 },
            },
          }}
          InputProps={{
            inputProps: { autoComplete: "off" },
          }}
        />

        <List dense={isMobile} sx={{ pt: 1 }}>
          {filtered.map((course) => {
            const isSelected = selectedCourses.some((i) => i.id === course.id);
            const color = isSelected ? "action.selected" : "transparent";

            let secondRow = "";
            if (course.instructor != null) {
              secondRow += course.instructor + " - ";
            }
            secondRow += "گروه " + course.group;

            return (
              <ListItemButton
                key={course.id}
                onClick={() => onSelect(course)}
                onPointerEnter={() => setPendingCourse(course)}
                onPointerLeave={() => setPendingCourse(null)}
                sx={{
                  backgroundColor: color,
                  borderRadius: 1,
                  mb: 0.5,
                  px: 1.5,
                  py: isMobile ? 1.5 : 1,
                  minHeight: isMobile ? 56 : 48,
                  "&:hover": {
                    backgroundColor: isSelected ? "action.selected" : "action.hover",
                  },
                }}
              >
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography
                    variant={isMobile ? "body1" : "body2"}
                    fontWeight={500}
                    sx={{ direction: "rtl", fontSize: { xs: 15, sm: 14 }, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
                  >
                    {`${course.name} - ${course.code}`}
                  </Typography>
                  <Typography
                    variant={isMobile ? "body2" : "caption"}
                    color="text.secondary"
                    sx={{ direction: "rtl", fontSize: { xs: 13, sm: 12 }, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
                  >
                    {secondRow}
                  </Typography>
                </Box>
                {isSelected && (
                  <Chip
                    label="انتخاب شده"
                    size="small"
                    color="primary"
                    variant="outlined"
                    sx={{
                      ml: 1,
                      height: isMobile ? 24 : 20,
                      fontSize: { xs: 11, sm: 10 },
                    }}
                  />
                )}
              </ListItemButton>
            );
          })}
        </List>
        {filtered.length === 0 && (
          <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 3 }}>
            درسی یافت نشد
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

export default CourseSelector;
