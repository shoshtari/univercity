import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Card,
  CardContent,
  Typography,
  Box,
} from "@mui/material";
import { useMediaQuery, useTheme } from "@mui/material";

function CourseTable({ courses }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  const totalUnits = courses.reduce((sum, course) => sum + course.units, 0);

  // Mobile card layout
  if (isMobile) {
    return (
      <Box sx={{ m: { xs: 1, sm: 2 }, width: "100%" }}>
        {courses.map((course) => (
          <Card key={course.id} variant="outlined" sx={{ mb: 1.5, px: 2, py: 1.5, minHeight: 48 }}>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 1 }}>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, minWidth: 0 }}>
                <Typography variant="body1" fontWeight={500} align="right" sx={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", maxWidth: "100%" }}>
                  {course.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" align="right" sx={{ whiteSpace: "nowrap" }}>
                  گروه {course.group}
                </Typography>
              </Box>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                {course.instructor && (
                  <Typography variant="caption" color="text.secondary" sx={{ whiteSpace: "nowrap" }}>
                    {course.instructor}
                  </Typography>
                )}
                <Typography variant="body2" fontWeight={600} color="primary.main" sx={{ whiteSpace: "nowrap", px: 1.5, py: 0.5, backgroundColor: "primary.light", borderRadius: 1, opacity: 0.3 }}>
                  {course.units} واحد
                </Typography>
              </Box>
            </Box>
          </Card>
        ))}
        <Card variant="outlined" sx={{ px: 2, py: 1.5, backgroundColor: "action.selected", border: "2px solid", borderColor: "primary.main" }}>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 1 }}>
            <Typography variant="body1" fontWeight={700} align="right">
              جمع واحدها
            </Typography>
            <Typography variant="h6" fontWeight={700} color="primary.main" sx={{ mb: 0 }}>
              {totalUnits} واحد
            </Typography>
          </Box>
        </Card>
      </Box>
    );
  }

  // Desktop table layout
  return (
    <TableContainer
      component={Paper}
      sx={{
        m: { xs: 1, sm: 2 },
        width: "100%",
        overflowX: "auto",
        border: "2px solid",
        borderRadius: 1,
      }}
    >
      <Table size="small" sx={{ minWidth: "auto" }}>
        <TableHead>
          <TableRow>
            <TableCell 
              align="right" 
              sx={{ 
                whiteSpace: "nowrap",
                fontWeight: 600,
                fontSize: 14,
                py: 1,
              }}
            >
              تعداد واحد
            </TableCell>
            <TableCell 
              align="right" 
              sx={{ 
                whiteSpace: "nowrap",
                fontWeight: 600,
                fontSize: 14,
                py: 1,
              }}
            >
              نام درس
            </TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {courses.map((i) => (
            <TableRow 
              key={i.id}
              sx={{
                "&:hover": {
                  bgcolor: "action.hover",
                },
              }}
            >
              <TableCell 
                align="right" 
                sx={{ 
                  whiteSpace: "nowrap",
                  fontSize: 13,
                  py: 1,
                  fontWeight: 500,
                }}
              >
                {i.units}
              </TableCell>
              <TableCell 
                align="right" 
                sx={{ 
                  fontSize: 13,
                  py: 1,
                }}
              >
                {i.name}
              </TableCell>
            </TableRow>
          ))}

          <TableRow
            sx={{
              borderTop: "2px solid",
              fontWeight: "bold",
              "& td": {
                py: 1,
                fontSize: 13,
              },
            }}
          >
            <TableCell align="right" sx={{ whiteSpace: "nowrap", fontWeight: 700 }}>
              {totalUnits}
            </TableCell>
            <TableCell align="right" sx={{ fontWeight: 700 }}>جمع واحدها</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </TableContainer>
  );
}
export default CourseTable;