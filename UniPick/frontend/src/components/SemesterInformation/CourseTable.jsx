import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from "@mui/material";

function CourseTable({ courses }) {
  return (
    <TableContainer
      component={Paper}
      sx={{
        ml: "auto",
        mr: "1%",
        mt: "5%",
        width: "fit-content",
        border: "2px solid",
      }}
    >
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell align="right">تعداد واحد</TableCell>
            <TableCell align="right">نام درس</TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {courses.map((i) => (
            <TableRow key={i.id}>
              <TableCell align="right">{i.units}</TableCell>
              <TableCell align="right">{i.name}</TableCell>
            </TableRow>
          ))}

          <TableRow
            sx={{
              borderTop: "2px solid",
              fontWeight: "bold",
            }}
          >
            <TableCell align="right">
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
