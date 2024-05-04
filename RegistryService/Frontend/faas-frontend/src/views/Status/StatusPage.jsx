import React, { Fragment, useEffect, useState } from "react";
import PropTypes from "prop-types";
import MainCard from "../../ui-component/cards/MainCard";
import {
  Avatar,
  Grid,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableFooter,
  TableHead,
  TablePagination,
  TableRow,
  Tooltip,
} from "@mui/material";
import { IconRefresh } from "@tabler/icons-react";
import { useTheme } from "@emotion/react";
import { Link } from "react-router-dom";
import { useSelector } from "react-redux";
import {
  DeleteOutline,
  KeyboardArrowLeft,
  KeyboardArrowRight,
  TextSnippetOutlined,
  FirstPageOutlined,
  LastPageOutlined,
} from "@mui/icons-material";
import axios from "axios";
import {
  API_BASE,
  DELETE_FUNCTION,
  GET_FUNCTIONS,
  LOG_PREFIX,
  LOG_SUFFIX,
  PORT,
} from "../../api/api";
import { useSnackbar } from "notistack";
import { Box } from "@mui/system";

export function TablePaginationActions(props) {
  const theme = useTheme();
  const { count, page, rowsPerPage, onPageChange } = props;

  const handleFirstPageButtonClick = (event) => {
    onPageChange(event, 0);
  };

  const handleBackButtonClick = (event) => {
    onPageChange(event, page - 1);
  };

  const handleNextButtonClick = (event) => {
    onPageChange(event, page + 1);
  };

  const handleLastPageButtonClick = (event) => {
    onPageChange(event, Math.max(0, Math.ceil(count / rowsPerPage) - 1));
  };

  return (
    <Box sx={{ flexShrink: 0, ml: 2.5 }}>
      <IconButton
        onClick={handleFirstPageButtonClick}
        disabled={page === 0}
        aria-label="first page"
      >
        {theme.direction === "rtl" ? (
          <LastPageOutlined />
        ) : (
          <FirstPageOutlined />
        )}
      </IconButton>
      <IconButton
        onClick={handleBackButtonClick}
        disabled={page === 0}
        aria-label="previous page"
      >
        {theme.direction === "rtl" ? (
          <KeyboardArrowRight />
        ) : (
          <KeyboardArrowLeft />
        )}
      </IconButton>
      <IconButton
        onClick={handleNextButtonClick}
        disabled={page >= Math.ceil(count / rowsPerPage) - 1}
        aria-label="next page"
      >
        {theme.direction === "rtl" ? (
          <KeyboardArrowLeft />
        ) : (
          <KeyboardArrowRight />
        )}
      </IconButton>
      <IconButton
        onClick={handleLastPageButtonClick}
        disabled={page >= Math.ceil(count / rowsPerPage) - 1}
        aria-label="last page"
      >
        {theme.direction === "rtl" ? (
          <FirstPageOutlined />
        ) : (
          <LastPageOutlined />
        )}
      </IconButton>
    </Box>
  );
}

TablePaginationActions.propTypes = {
  count: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
  page: PropTypes.number.isRequired,
  rowsPerPage: PropTypes.number.isRequired,
};

const getTimeDifference = (date) => {
  console.log(date);
  if (date) {
    date = new Date(date);
    const diffInMilliseconds = Date.now() - date.getTime();
    const diffInSeconds = Math.floor(diffInMilliseconds / 1000);
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);
    const diffInWeeks = Math.floor(diffInDays / 7);
    const diffInMonths = Math.floor(diffInWeeks / 4);
    const diffInYears = Math.floor(diffInMonths / 12);
    const diffInDecades = Math.floor(diffInYears / 10);
    const diffInCenturies = Math.floor(diffInDecades / 10);
    if (diffInCenturies > 0) {
      return `${diffInCenturies} centur${
        diffInCenturies > 1 ? "ies" : "y"
      } ago`;
    } else if (diffInDecades > 0) {
      return `${diffInDecades} decade${diffInDecades > 1 ? "s" : ""} ago`;
    } else if (diffInYears > 0) {
      return `${diffInYears} year${diffInYears > 1 ? "s" : ""} ago`;
    } else if (diffInMonths > 0) {
      return `${diffInMonths} month${diffInMonths > 1 ? "s" : ""} ago`;
    } else if (diffInWeeks > 0) {
      return `${diffInWeeks} week${diffInWeeks > 1 ? "s" : ""} ago`;
    } else if (diffInDays > 0) {
      return `${diffInDays} day${diffInDays > 1 ? "s" : ""} ago`;
    } else if (diffInHours > 0) {
      return `${diffInHours} hour${diffInHours > 1 ? "s" : ""} ago`;
    } else if (diffInMinutes > 0) {
      return `${diffInMinutes} minute${diffInMinutes > 1 ? "s" : ""} ago`;
    } else if (diffInSeconds > 0) {
      return `${diffInSeconds} second${diffInSeconds > 1 ? "s" : ""} ago`;
    } else {
      return "Just now";
    }
  }
  return "Never";
};

export const fetchData = async (url) => {
  try {
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    // Handle error
    console.error("Error fetching data:", error);
    throw error; // Rethrow so the caller can handle it
  }
};
export const deleteData = async (url, data) => {
  try {
    const response = await axios.delete(url, { data: data });
    console.log(response);
    return response.data;
  } catch (error) {
    // Handle error
    console.error("Error deleting:", error);
    throw error; // Rethrow so the caller can handle it
  }
};
const StatusPage = () => {
  const theme = useTheme();
  const functions = useSelector((state) => state.log);
  const [functionData, setFunctionData] = useState([]);
  const { enqueueSnackbar } = useSnackbar();
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(5);

  // Avoid a layout jump when reaching the last page with empty rows.
  const emptyRows =
    page > 0 ? Math.max(0, (1 + page) * rowsPerPage - functionData.length) : 0;

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  useEffect(() => {
    fetchData(API_BASE + PORT + GET_FUNCTIONS)
      .then((responseData) => {
        setFunctionData(responseData);
        enqueueSnackbar("Logs fetched", {
          variant: "success",
          anchorOrigin: {
            vertical: "bottom",
            horizontal: "center",
          },
        });
      })
      .catch((error) => {
        console.log(error);
        enqueueSnackbar(error.message, {
          variant: "error",
          anchorOrigin: {
            vertical: "bottom",
            horizontal: "center",
          },
        });
      });
  }, []);
  const refreshData = () => {
    console.log("refreshing data");
    fetchData(API_BASE + PORT + GET_FUNCTIONS)
      .then((responseData) => {
        setFunctionData(responseData);
        enqueueSnackbar("Logs refreshed", {
          variant: "success",
          anchorOrigin: {
            vertical: "bottom",
            horizontal: "center",
          },
        });
      })
      .catch((error) => {
        console.log(error);
        enqueueSnackbar(error.message, {
          variant: "error",
          anchorOrigin: {
            vertical: "bottom",
            horizontal: "center",
          },
        });
      });
  };
  const deleteHandler = (fnName) => {
    console.log(fnName);
    deleteData(API_BASE + PORT + DELETE_FUNCTION + fnName)
      .then((responseData) => {
        enqueueSnackbar("Function deleted successfully!", {
          variant: "success",
          anchorOrigin: {
            vertical: "bottom",
            horizontal: "center",
          },
        });
        setFunctionData((prevFunctionData) => {
          return prevFunctionData.filter((func) => func.fnName !== fnName);
        });
      })
      .catch((error) => {
        console.log(error);
        enqueueSnackbar(error.message, {
          variant: "error",
          anchorOrigin: {
            vertical: "bottom",
            horizontal: "center",
          },
        });
      });
  };
  const getStatusChipColor = (status) => {
    switch (status) {
      case "PROCESSING":
        return {
          bgcolor: theme.palette.warning.main,
        };
      case "SUCCESS":
        return {
          bgcolor: theme.palette.success.main,
        };
      case "FAILED":
        return {
          bgcolor: theme.palette.error.main,
        };
      case "CREATED":
        return {
          bgcolor: "#b8b8b8",
        };
      default:
        return {
          bgcolor: theme.palette.secondary.main,
        };
    }
  };
  return (
    <>
      <MainCard
        title="Function Logs"
        secondary={
          <Tooltip title="refresh" placement="left">
            <IconButton aria-label="refresh" onClick={refreshData}>
              <IconRefresh />
            </IconButton>
          </Tooltip>
        }
      >
        <TableContainer component={Paper}>
          <Table aria-label="log-table">
            <TableHead>
              <TableRow>
                <TableCell>Sl No.</TableCell>
                <TableCell>Function Name</TableCell>
                <TableCell>Trigger Type</TableCell>
                <TableCell>Event Type</TableCell>
                <TableCell>Last Triggered</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="center">Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(rowsPerPage > 0
                ? functionData.slice(
                    page * rowsPerPage,
                    page * rowsPerPage + rowsPerPage
                  )
                : functionData
              ).map((row, index) => (
                <TableRow
                  key={row.fnId}
                  sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
                >
                  <TableCell>{index + 1}</TableCell>
                  <TableCell>{row.fnName}</TableCell>
                  <TableCell>{row.triggerType}</TableCell>
                  <TableCell>{row.eventType}</TableCell>
                  <TableCell>{getTimeDifference(row.triggerTime)}</TableCell>
                  <TableCell>
                    <Tooltip title={row.status} placement="right-start">
                      <Avatar
                        sx={{
                          ...getStatusChipColor(row.status),
                          height: 24,
                          width: 24,
                        }}
                      >
                        {" "}
                      </Avatar>
                    </Tooltip>
                  </TableCell>
                  <TableCell align="center">
                    <Grid container justifyContent={"center"} spacing={0.5}>
                      <Grid item>
                        <Tooltip title="logs" placement="bottom">
                          <Link
                            to={LOG_PREFIX + row.fnName + LOG_SUFFIX}
                            rel="noopener"
                            target="_blank"
                          >
                            <IconButton aria-label="logs" color="primary">
                              <TextSnippetOutlined />
                            </IconButton>
                          </Link>
                        </Tooltip>
                      </Grid>
                      <Grid item>
                        <Tooltip title="delete" placement="bottom">
                          <IconButton
                            aria-label="delete"
                            color="error"
                            id={row.fnName}
                            onClick={(event) =>
                              deleteHandler(event.target.parentElement.id)
                            }
                          >
                            <DeleteOutline />
                          </IconButton>
                        </Tooltip>
                      </Grid>
                    </Grid>
                  </TableCell>
                </TableRow>
              ))}
              {emptyRows > 0 && (
                <TableRow style={{ height: 53 * emptyRows }}>
                  <TableCell colSpan={6} />
                </TableRow>
              )}
            </TableBody>
            <TableFooter>
              <TableRow>
                <TablePagination
                  rowsPerPageOptions={[5, 10, 15, { label: "All", value: -1 }]}
                  colSpan={12}
                  count={functionData.length}
                  rowsPerPage={rowsPerPage}
                  page={page}
                  slotProps={{
                    select: {
                      inputProps: {
                        "aria-label": "rows per page",
                      },
                      native: true,
                    },
                  }}
                  onPageChange={handleChangePage}
                  onRowsPerPageChange={handleChangeRowsPerPage}
                  ActionsComponent={TablePaginationActions}
                />
              </TableRow>
            </TableFooter>
          </Table>
        </TableContainer>{" "}
      </MainCard>
    </>
  );
};

export default StatusPage;
