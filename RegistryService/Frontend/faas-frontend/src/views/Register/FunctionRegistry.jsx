import * as React from "react";
import Box from "@mui/material/Box";
import Stepper from "@mui/material/Stepper";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import MainCard from "../../ui-component/cards/MainCard";
import BasicForm from "./BasicForm";
import { useRef } from "react";
import CodeEditor from "./CodeEditor";
const steps = ["Basic Details", "Code"];

import axios from "axios";
import { useSelector, useDispatch, shallowEqual } from "react-redux";
import { useSnackbar } from "notistack";
import { Buffer } from "buffer";
import { API_BASE, PORT, REGISTER } from "../../api/api";
import { ADD_FUNCTION } from "../../store/actions";
import { CircularProgress } from "@mui/material";
const registerFunc = async (url, data) => {
  try {
    // Convert code and deps to base64 encoding
    const base64Code = Buffer.from(data.code).toString("base64");
    const base64Deps = Buffer.from(data.deps).toString("base64");
    console.log(data);
    // Send POST request with base64-encoded data
    const response = await axios.post(url, {
      fnName: data.functionName,
      runtime: data.runtime,
      sourceCode: base64Code,
      requirements: base64Deps,
      entryFn: data.entryFn,
      triggerType: "CLOUD_STORAGE",
      eventType: data.eventType,
      bucketName: data.bucketId,
    });

    // Handle response
    console.log("Response:", response.data);
    return response.data;
  } catch (error) {
    // Handle error
    console.error("Error posting data:", error);
    throw error; // Rethrow so the caller can handle it
  }
};

export default function FunctionRegistry() {
  const [activeStep, setActiveStep] = React.useState(0);
  const [isUploading, setIsUploading] = React.useState(false);
  const basicformRef = useRef(null);
  const codeformRef = useRef(null);
  const basicDetails = useSelector((state) => state.basicform);
  const code = useSelector((state) => state.code);
  React.useEffect(() => {
    if (activeStep === 1) {
      setIsUploading(true);
      registerFunc(API_BASE + PORT + REGISTER, { ...basicDetails, ...code })
        .then((responseData) => {
          console.log(responseData);
          enqueueSnackbar(responseData, {
            variant: "success",
            anchorOrigin: {
              vertical: "bottom",
              horizontal: "center",
            },
          });
          setActiveStep((prevActiveStep) => prevActiveStep + 1);
          setIsUploading(false);
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
          setIsUploading(false);
        });
    }
  }, [code]);

  const { enqueueSnackbar } = useSnackbar();
  const dispatch = useDispatch();
  const handleNext = () => {
    if (activeStep === 0) {
      basicformRef.current?.handleSubmit();
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
    } else {
      codeformRef.current?.handleSubmit();
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
  };

  return (
    <MainCard>
      <Box sx={{ width: "100%" }}>
        <Stepper activeStep={activeStep}>
          {steps.map((label, index) => {
            const stepProps = {};
            const labelProps = {};
            return (
              <Step key={label} {...stepProps}>
                <StepLabel {...labelProps}>{label}</StepLabel>
              </Step>
            );
          })}
        </Stepper>
        {activeStep === steps.length ? (
          <React.Fragment>
            <Typography sx={{ mt: 2, mb: 1 }}>All steps completed</Typography>
            <Box sx={{ display: "flex", flexDirection: "row", pt: 2 }}>
              <Box sx={{ flex: "1 1 auto" }} />
              <Button onClick={handleReset}>Reset</Button>
            </Box>
          </React.Fragment>
        ) : (
          <React.Fragment>
            <Typography sx={{ mt: 2, mb: 1 }}>Step {activeStep + 1}</Typography>
            {activeStep === 0 && <BasicForm innerRef={basicformRef} />}
            {activeStep === 1 && <CodeEditor ref={codeformRef} />}
            <Box
              sx={{
                display: "flex",
                flexDirection: "row",
                pt: 2,
              }}
            >
              <Button
                color="inherit"
                disabled={activeStep === 0}
                onClick={handleBack}
                sx={{ mr: 1 }}
              >
                Back
              </Button>
              <Box sx={{ flex: "1 1 auto" }} />
              <Button onClick={handleNext} disabled={isUploading}>
                {activeStep === steps.length - 1 ? "Finish" : "Next"}
                {isUploading && (
                  <CircularProgress
                    size={24}
                    sx={{
                      color: "primary",
                      position: "absolute",
                      top: "50%",
                      left: "50%",
                      marginTop: "-12px",
                      marginLeft: "-12px",
                    }}
                  />
                )}
              </Button>
            </Box>
          </React.Fragment>
        )}
      </Box>
    </MainCard>
  );
}
