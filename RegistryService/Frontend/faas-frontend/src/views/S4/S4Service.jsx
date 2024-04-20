import React, { useState } from "react";
import CardSecondaryAction from "../../ui-component/cards/CardSecondaryAction";
import {
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Fab,
  Grid,
  IconButton,
  Modal,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableFooter,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Tooltip,
  Typography,
  circularProgressClasses,
} from "@mui/material";
import SubCard from "../../ui-component/cards/SubCard";
import { Box, minWidth, width } from "@mui/system";
import {
  AddCircleOutlined,
  CloudDownloadOutlined,
  DeleteForeverOutlined,
  DeleteOutline,
  FileUploadOutlined,
} from "@mui/icons-material";
import CancelIcon from "@mui/icons-material/Cancel";
import { SnackbarProvider, useSnackbar } from "notistack";
import {
  API_BASE,
  CREATE_BUCKET,
  DELETE_BUCKET,
  DELETE_IMAGE,
  FETCH_BUCKET,
  PORT2,
  UPLOAD,
} from "../../api/api";
import axios from "axios";
import { useNavigate } from "react-router";
import SearchBar from "../SearchSection/SearchBar";
import MainCard from "../../ui-component/cards/MainCard";
import {
  TablePaginationActions,
  deleteData,
  fetchData,
} from "../../views/Status/StatusPage";
import { IconRefresh } from "@tabler/icons-react";
// axios.defaults.timeout = 15000;
const uploadImg = async (url, data) => {
  try {
    console.log(data);
    // Send POST request with base64-encoded data
    const response = await axios.post(url, { ...data });

    // Handle response
    console.log("Response:", response.data);
    return response.data;
  } catch (error) {
    // Handle error
    console.error("Error posting data:", error);
    throw error; // Rethrow so the caller can handle it
  }
};
const createBucket = async (url, bucketID) => {
  try {
    // Send POST request with base64-encoded data
    const response = await axios.post(url + "/" + bucketID);

    // Handle response
    console.log("Response:", response.data);
    return response.data;
  } catch (error) {
    // Handle error
    console.error("Error posting data:", error);
    throw error; // Rethrow so the caller can handle it
  }
};
const modalstyle = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: 400,
  bgcolor: "background.paper",
  border: "2px solid #000",
  boxShadow: 24,
  p: 4,
};

const S4Service = () => {
  const [bucketID, setBucketID] = useState("");
  const [files, setFiles] = useState([]);
  const [base64Data, setBase64Data] = useState([]);
  const { enqueueSnackbar } = useSnackbar();
  const [allImageData, setAllImageData] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [createopen, setCreateOpen] = useState(false);
  const handleCreateModalOpen = () => setCreateOpen(true);
  const handleCreateModalClose = () => {
    setBucketID("");
    setCreateOpen(false);
  };
  const [uploadopen, setUploadOpen] = useState(false);
  const handleUploadModalOpen = () => setUploadOpen(true);
  const handleUploadModalClose = () => setUploadOpen(false);
  const [deleteopen, setDeleteOpen] = useState(false);
  const handleDeleteModalOpen = () => setDeleteOpen(true);
  const handleDeleteModalClose = () => setDeleteOpen(false);
  // Pagination handlers
  // Avoid a layout jump when reaching the last page with empty rows.
  const getEmptyRows = () => {
    return page > 0
      ? Math.max(0, (1 + page) * rowsPerPage - allImageData.length)
      : 0;
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  // Search handler
  const doSearch = (bucket_id) => {
    showBucket(bucket_id);
  };
  const addImageHandler = () => {
    handleUploadModalOpen();
  };
  const bucketDeleteHandler = () => {
    handleDeleteModalOpen();
  };
  // Bucket creation and deletio
  const showCreateDialog = () => {
    handleCreateModalOpen();
  };
  const bucketCreateActual = () => {
    handleCreateModalClose();
    enqueueSnackbar("Trying to create bucket", {
      variant: "info",
      anchorOrigin: {
        vertical: "bottom",
        horizontal: "center",
      },
    });
    createBucket(API_BASE + PORT2 + CREATE_BUCKET, bucketID)
      .then((responseData) => {
        enqueueSnackbar(responseData, {
          variant: "success",
          anchorOrigin: {
            vertical: "bottom",
            horizontal: "center",
          },
        });
      })
      .catch((error) => {
        enqueueSnackbar(error.message, {
          variant: "error",
          anchorOrigin: {
            vertical: "bottom",
            horizontal: "center",
          },
        });
      });
  };
  const bucketDeleteActual = () => {
    handleDeleteModalClose();
    deleteData(API_BASE + PORT2 + DELETE_BUCKET + bucketID)
      .then((responseData) => {
        enqueueSnackbar("Bucket deleted successfully!", {
          variant: "success",
          anchorOrigin: {
            vertical: "bottom",
            horizontal: "center",
          },
        });
        setBucketID("");
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
  // Refresh table data
  const refreshHandle = () => {
    showBucket(bucketID);
  };
  // Fetch bucket data
  const showBucket = (id) => {
    setBucketID(id);
    fetchData(API_BASE + PORT2 + FETCH_BUCKET + id)
      .then((responseData) => {
        setAllImageData(responseData);
        enqueueSnackbar("Bucket fetched", {
          variant: "success",
          anchorOrigin: {
            vertical: "bottom",
            horizontal: "center",
          },
        });
      })
      .catch((error) => {
        console.log(error);
        if (error.response.status == 500) {
          enqueueSnackbar(error.response.data, {
            variant: "warning",
            anchorOrigin: {
              vertical: "bottom",
              horizontal: "center",
            },
          });

          showCreateDialog();
        } else {
          enqueueSnackbar(error.message, {
            variant: "error",
            anchorOrigin: {
              vertical: "bottom",
              horizontal: "center",
            },
          });
        }
      });
  };
  const handleFileChange = (event) => {
    const selectedFiles = Array.from(event.target.files);
    setFiles(selectedFiles);
    const promises = selectedFiles.map((file) => readFileAsBase64(file));
    Promise.all(promises).then((data) => {
      setBase64Data(data);
    });
  };
  const readFileAsBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result.split(",")[1]);
      reader.onerror = (error) => reject(error);
      reader.readAsDataURL(file);
    });
  };
  // Image upload to bucket
  const handleSubmit = () => {
    // Post base64 encoded data to the server
    // console.log("Base64 encoded data:");
    // for (let index = 0; index < base64Data.length; index++) {
    //   const element = base64Data[index];
    //   console.log(element);
    // }
    setIsUploading(true);
    // uploadImg(API_BASE + PORT2 + UPLOAD, {
    //   bucketName: bucketID,
    //   base64Images: base64Data,
    // })
    //   .then((responseData) => {
    //     enqueueSnackbar("Upload Successful", {
    //       variant: "success",
    //       anchorOrigin: {
    //         vertical: "bottom",
    //         horizontal: "center",
    //       },
    //     });
    //     setIsUploading(false);
    //     setBase64Data([]);
    //     setFiles([]);
    //     handleUploadModalClose();
    //   })
    //   .catch((error) => {
    //     setIsUploading(false);
    //     enqueueSnackbar(error.message, {
    //       variant: "error",
    //       anchorOrigin: {
    //         vertical: "bottom",
    //         horizontal: "center",
    //       },
    //     });
    //   });
  };
  // Cancel upload
  const cancelHandler = () => {
    if (!isUploading) {
      setBase64Data([]);
      setFiles([]);
    }
  };
  // Download image to local
  const handleDownload = async (imageData, imageName) => {
    try {
      // Convert base64 image data to Blob
      const response = await axios.get(imageData, { responseType: "blob" });
      const blob = new Blob([response.data], { type: "image/jpeg" }); // Adjust type as needed

      // Create a temporary link element to trigger the download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = imageName; // Set the filename for download
      document.body.appendChild(link);
      link.click();

      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
    } catch (error) {
      console.error("Download Error:", error);
    }
  };
  // Delete image from bucket
  const deleteHandler = (id) => {
    console.log(id);
    deleteData(API_BASE + PORT2 + DELETE_IMAGE, {
      bucketName: bucketID,
      imageId: id,
    })
      .then((responseData) => {
        enqueueSnackbar("Image deleted successfully!", {
          variant: "success",
          anchorOrigin: {
            vertical: "bottom",
            horizontal: "center",
          },
        });
        setAllImageData((prevImageData) => {
          return prevImageData.filter((img) => img.file_id != id);
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
  const fileNames = files.map((file) => file.name).join(", ");

  return (
    <Stack
      direction="column"
      justifyContent="center"
      alignItems="center"
      spacing={2}
    >
      <SubCard
        content={true}
        darkTitle={true}
        title="S4 Bucket"
        sx={{ width: "50%" }}
      >
        <SearchBar doSearch={doSearch} />
      </SubCard>
      {bucketID && (
        <MainCard
          sx={{ minWidth: "80%" }}
          title={"Bucket-" + bucketID}
          secondary={
            <Stack direction="row">
              <Tooltip title="Add Image" placement="left" color="primary">
                <IconButton aria-label="refresh" onClick={addImageHandler}>
                  <AddCircleOutlined />
                </IconButton>
              </Tooltip>
              <Tooltip title="Delete Bucket" placement="bottom">
                <IconButton
                  aria-label="Delete"
                  onClick={bucketDeleteHandler}
                  color="error"
                >
                  <DeleteForeverOutlined />
                </IconButton>
              </Tooltip>
              <Tooltip title="Refresh" placement="right" color="secondary">
                <IconButton aria-label="Refresh" onClick={refreshHandle}>
                  <IconRefresh />
                </IconButton>
              </Tooltip>
            </Stack>
          }
        >
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Sl No.</TableCell>
                  <TableCell>Image ID</TableCell>
                  <TableCell>Image</TableCell>
                  <TableCell>Additional Info</TableCell>
                  <TableCell>Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(rowsPerPage > 0
                  ? allImageData.slice(
                      page * rowsPerPage,
                      page * rowsPerPage + rowsPerPage
                    )
                  : allImageData
                ).map((row, index) => (
                  <TableRow
                    key={row.file_id}
                    sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
                  >
                    <TableCell>{index + 1}</TableCell>
                    <TableCell>{row.file_id}</TableCell>
                    <TableCell>
                      <img
                        src={`data:image/jpeg;base64,${row.image}`}
                        alt={row.file_id}
                        style={{ width: "250px", height: "auto" }}
                        loading="lazy"
                      />
                    </TableCell>
                    <TableCell>{row.additional_info}</TableCell>
                    <TableCell>
                      <Grid container spacing={0.5}>
                        <Grid item>
                          <Tooltip title="Download" placement="bottom">
                            <IconButton
                              aria-label="logs"
                              color="primary"
                              onClick={() =>
                                handleDownload(
                                  row.image,
                                  "Image-" + row.file_id
                                )
                              }
                            >
                              <CloudDownloadOutlined />
                            </IconButton>
                          </Tooltip>
                        </Grid>
                        <Grid item>
                          <Tooltip title="Delete Image" placement="bottom">
                            <IconButton
                              aria-label="delete"
                              color="error"
                              id={row.file_id}
                              onClick={(event) => deleteHandler(row.file_id)}
                            >
                              <DeleteOutline />
                            </IconButton>
                          </Tooltip>
                        </Grid>
                      </Grid>
                    </TableCell>
                  </TableRow>
                ))}
                {getEmptyRows() > 0 && (
                  <TableRow style={{ height: 53 * getEmptyRows() }}>
                    <TableCell colSpan={6} />
                  </TableRow>
                )}
              </TableBody>
              <TableFooter>
                <TableRow>
                  <TablePagination
                    rowsPerPageOptions={[
                      5,
                      10,
                      15,
                      { label: "All", value: -1 },
                    ]}
                    colSpan={6}
                    count={allImageData.length}
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
                  ></TablePagination>
                </TableRow>
              </TableFooter>
            </Table>
          </TableContainer>
        </MainCard>
      )}

      {/* Upload image modal */}
      <Modal
        open={uploadopen}
        onClose={handleUploadModalClose}
        aria-labelledby="modal-upload-image"
        aria-describedby="modal-upload-image-to-bucket"
      >
        <SubCard
          content={true}
          darkTitle={true}
          title="Upload To Bucket"
          sx={modalstyle}
        >
          <Grid container spacing={2}>
            <Grid item>
              <Grid container spacing={2}>
                <Grid item>
                  <TextField
                    fullWidth
                    disabled
                    id="file"
                    value={fileNames}
                    label="Upload Files"
                    InputProps={{
                      startAdornment: (
                        <IconButton component="label">
                          <FileUploadOutlined />
                          <input
                            accept="image/*"
                            styles={{ display: "none" }}
                            type="file"
                            hidden
                            name="File"
                            multiple
                            onChange={handleFileChange}
                          />
                        </IconButton>
                      ),
                      endAdornment: (
                        <IconButton onClick={cancelHandler}>
                          <CancelIcon />
                        </IconButton>
                      ),
                    }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ mt: 2 }}>
                    <Button
                      disabled={base64Data.length === 0}
                      disableElevation
                      variant="contained"
                      color="secondary"
                      onClick={handleSubmit}
                      fullWidth
                    >
                      Upload
                      {!isUploading && (
                        <CircularProgress
                          variant="indeterminate"
                          disableShrink
                          size={40}
                          thickness={4}
                        />
                      )}
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </SubCard>
      </Modal>
      {/* Delete bucket confirmation dialog */}
      <Dialog
        open={deleteopen}
        onClose={handleDeleteModalClose}
        aria-labelledby="alert-dialog-delete-bucket"
        aria-describedby="alert-dialog-delete-bucket"
      >
        <DialogTitle id="alert-dialog-title">
          <Typography
            sx={{
              fontSize: "1.0rem",
              fontWeight: 500,
            }}
          >
            {" "}
            {"Delete bucket " + bucketID + " ?"}
          </Typography>
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Are you sure that you want to delete bucket {bucketID} and all of
            its contents?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteModalClose}>Cancel</Button>
          <Button onClick={bucketDeleteActual}>Yes</Button>
        </DialogActions>
      </Dialog>
      {/* Create bucket confirmation dialog */}
      <Dialog
        open={createopen}
        onClose={handleCreateModalClose}
        aria-labelledby="alert-dialog-delete-bucket"
        aria-describedby="alert-dialog-delete-bucket"
      >
        <DialogTitle id="alert-dialog-title">
          <Typography
            sx={{
              fontSize: "1.0rem",
              fontWeight: 500,
            }}
          >
            {"Bucket " + bucketID + " not found !!"}
          </Typography>
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Do you want to create bucket {bucketID}?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCreateModalClose}>No</Button>
          <Button onClick={bucketCreateActual}>Yes</Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
};

export default S4Service;
