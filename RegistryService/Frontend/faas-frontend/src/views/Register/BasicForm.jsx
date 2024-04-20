import * as Yup from "yup";
import { Formik } from "formik";
import React, { useState } from "react";
import { Button, FormControl, Grid, MenuItem, TextField } from "@mui/material";
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
            <Grid container spacing={2}>
              <Grid item>
                <TextField
                  id="functionName"
                  label="Function Name"
                  margin="normal"
                  name="functionName"
                  type="text"
                  defaultValue=""
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
                  defaultValue="Cloud Storage"
                />
              </Grid>
            </Grid>
            <Grid container spacing={2}>
              <Grid item sx={{ width: 222 }}>
                <TextField
                  id="eventType"
                  name="eventType"
                  margin="normal"
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
                  onChange={handleChange}
                />
              </Grid>
            </Grid>
            {/* <Box sx={{ mt: 2 }}>
              <Button
                id="submit"
                disableElevation
                disabled={isSubmitting}
                size="large"
                type="submit"
                variant="contained"
                color="secondary"
              >
                Submit
              </Button>
            </Box> */}
          </form>
        )}
      </Formik>
    </>
  );
};

export default BasicForm;
