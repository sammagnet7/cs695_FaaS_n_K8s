import * as Yup from "yup";
import { Formik } from "formik";
import React, { useState } from "react";
import {
  Button,
  FormControl,
  Grid,
  InputAdornment,
  MenuItem,
  TextField,
  Typography,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { Box } from "@mui/system";
import AnimateButton from "../../ui-component/extended/AnimateButton";
import { useDispatch } from "react-redux";
import { SAVE_FORM_BASIC } from "../../store/actions";
const BasicForm = ({ innerRef }) => {
  const theme = useTheme();
  const [etype, setEType] = useState("");

  const dispatch = useDispatch();
  return (
    <>
      <Formik
        innerRef={innerRef}
        initialValues={{
          functionName: "",
          trigger: "Cloud Storage",
          eventType: "",
          bucketId: "",
          instances: "5",
          cpu: "0.5",
          memory: "512",
        }}
        onSubmit={(values, { setErrors, setStatus, setSubmitting }) => {
          console.log(values);
          dispatch({ type: SAVE_FORM_BASIC, ...values });
          setSubmitting(false);
        }}
      >
        {({
          errors,
          handleBlur,
          handleChange,
          handleSubmit,
          isSubmitting,
          touched,
          values,
        }) => (
          <form onSubmit={handleSubmit}>
            <Grid container spacing={8}>
              <Grid item>
                <Typography
                  sx={{
                    fontSize: "1rem",
                    fontWeight: 700,
                    mr: 1,
                    mt: 1.75,
                  }}
                >
                  Basic Details
                </Typography>
                <Grid container spacing={2}>
                  <Grid item>
                    <TextField
                      id="functionName"
                      label="Function Name"
                      margin="normal"
                      name="functionName"
                      type="text"
                      value={values.functionName}
                      onChange={handleChange}
                    />
                  </Grid>
                  <Grid item>
                    <TextField
                      disabled
                      id="trigger"
                      label="Trigger"
                      margin="normal"
                      name="trigger"
                      type="text"
                      onChange={handleChange}
                      value={values.trigger}
                    />
                  </Grid>
                </Grid>
                <Grid container spacing={2}>
                  <Grid item sx={{ width: 222 }}>
                    <TextField
                      id="eventType"
                      name="eventType"
                      margin="normal"
                      value={values.eventType}
                      onChange={handleChange}
                      select
                      label="Select trigger event type"
                      fullWidth
                    >
                      <MenuItem key="Upload" value="UPLOAD_INTO_BUCKET">
                        Upload
                      </MenuItem>
                      {/* <MenuItem key="Update" value="Update">
                    Update
                  </MenuItem>
                  <MenuItem key="Delete" value="Delete">
                    Delete
                  </MenuItem> */}
                    </TextField>
                  </Grid>
                  <Grid item>
                    <TextField
                      id="bucketId"
                      label="Bucket ID"
                      margin="normal"
                      name="bucketId"
                      value={values.bucketId}
                      onChange={handleChange}
                    />
                  </Grid>
                </Grid>
              </Grid>
              <Grid item>
                <Typography
                  sx={{
                    fontSize: "1rem",
                    fontWeight: 700,
                    mr: 1,
                    mt: 1.75,
                  }}
                >
                  Resource
                </Typography>
                <Grid container spacing={2}>
                  <Grid item>
                    <TextField
                      id="cpu"
                      label="Max vCPU"
                      margin="normal"
                      name="cpu"
                      type="number"
                      value={values.cpu}
                      onChange={handleChange}
                    />
                  </Grid>
                  <Grid item>
                    <TextField
                      id="memory"
                      label="Max memory"
                      margin="normal"
                      name="memory"
                      type="number"
                      value={values.memory}
                      onChange={handleChange}
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">Mi</InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                </Grid>
                <Grid container spacing={2}>
                  <Grid item>
                    <TextField
                      id="instances"
                      label="Max instance"
                      margin="normal"
                      name="instances"
                      type="number"
                      value={values.instances}
                      onChange={handleChange}
                    />
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          </form>
        )}
      </Formik>
    </>
  );
};

export default BasicForm;
