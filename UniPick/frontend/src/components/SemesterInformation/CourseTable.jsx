import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from "@mui/material";
import { useMediaQuery, useTheme } from "@mui/material";

function CourseTable({ courses }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  return (
    <TableContainer
      component={Paper}
      sx={{
        m: { xs: 1, sm: 2 },
        width: "100%",
        overflowX: "auto",
        border: "2px solid",
      }}
    >
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell align="right" sx={{ whiteSpace: "nowrap" }}>تعداد واحد</TableCell>
            <TableCell align="right" sx={{ whiteSpace: "nowrap" }}>نام درس</TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {courses.map((i) => (
            <TableRow key={i.id}>
              <TableCell align="right" sx={{ whiteSpace: "nowrap" }}>{i.units}</TableCell>
              <TableCell align="right">{i.name}</TableCell>
            </TableRow>
          ))}

          <TableRow
            sx={{
              borderTop: "2px solid",
              fontWeight: "bold",
            }}
          >
            <TableCell align="right" sx={{ whiteSpace: "nowrap" }}>
              {courses.reduce((sum, course) => sum + course.units, 0)}
            </TableCell>
            <TableCell align="right">جمع واحدها</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </TableContainer>
  );
}
export default CourseTable;