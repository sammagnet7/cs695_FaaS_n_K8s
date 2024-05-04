import React, { forwardRef, useEffect, useImperativeHandle } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { vscodeDark } from "@uiw/codemirror-theme-vscode";
import { python } from "@codemirror/lang-python";
import { useState, useCallback } from "react";
import TextSnippetIcon from "@mui/icons-material/TextSnippet";
import CodeIcon from "@mui/icons-material/Code";
import {
  Grid,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  MenuItem,
  Paper,
  TextField,
  Typography,
} from "@mui/material";
import { useDispatch } from "react-redux";
import { SAVE_CODE_DEPS } from "../../store/actions";
import { CODE, REQUIREMENTS } from "../../store/constant";
const CodeEditor = forwardRef((props, ref) => {
  const [codeValue, setcodeValue] = useState(CODE);
  const [dependencyValue, setDependencyValue] = useState(REQUIREMENTS);
  const [detectedFns, setDetectedFns] = useState([]);
  const [entrypoint, setEntryPoint] = useState("userDefinedFunction");
  const regex = /def\s+(\w+)\s*\((\w*)\)\:/g;
  useEffect(() => {
    const matches = [...codeValue.matchAll(regex)];
    const functionNames = matches.map((match) => match[1]);
    setDetectedFns(functionNames);
  }, [codeValue]);

  const entryPointChange = (event) => {
    setEntryPoint(event.target.value);
  };
  const [files, setFiles] = useState([
    { name: "app.py", content: codeValue, icon: <CodeIcon /> },
    {
      name: "requirements.txt",
      content: dependencyValue,
      icon: <TextSnippetIcon />,
    },
  ]);
  const [activeFileIndex, setActiveFileIndex] = useState(0);
  const dispatch = useDispatch();
  const handleSubmit = () => {
    dispatch({
      type: SAVE_CODE_DEPS,
      ...{
        code: files[0].content,
        deps: files[1].content,
        entryFn: entrypoint,
        runtime: "python",
      },
    });
  };
  useImperativeHandle(ref, () => {
    return {
      handleSubmit,
    };
  });
  const handleFileSelect = (file) => {
    const index = files.findIndex((f) => f.name === file.name);
    setActiveFileIndex(index);
  };
  useEffect(() => {
    const updatedFiles = [...files];
    updatedFiles[1].content = dependencyValue;
    setFiles(updatedFiles);
  }, [dependencyValue]);

  useEffect(() => {
    const updatedFiles = [...files];
    updatedFiles[0].content = codeValue;
    setFiles(updatedFiles);
  }, [codeValue]);

  const onChange = (val, viewUpdate) => {
    if (activeFileIndex === 0) {
      setcodeValue(val);
    } else if (activeFileIndex === 1) {
      setDependencyValue(val);
    }
  };
  return (
    <>
      <Grid container>
        <Grid item sx={{ mt: 1.75, mb: 1 }} xs={12} sm={12} md={6}>
          <TextField
            disabled
            id="runtime-select"
            select
            label="Runtime Type"
            defaultValue="Python"
            sx={{ width: "35%" }}
          >
            <MenuItem key={"runtime"} value={"Python"}>
              Python
            </MenuItem>
          </TextField>
        </Grid>
        <Grid item sx={{ mt: 1.75, mb: 1 }} xs={12} sm={12} md={6}>
          <TextField
            id="entrypoint-select"
            select
            value={entrypoint}
            onChange={entryPointChange}
            label="Entrypoint"
            sx={{ width: "35%" }}
          >
            {detectedFns.map((fnName, index) => (
              <MenuItem key={index} value={fnName}>
                {fnName}
              </MenuItem>
            ))}
          </TextField>
        </Grid>
      </Grid>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Paper>
            <Typography
              sx={{
                fontSize: "2.5 rem",
                fontWeight: 700,
                mr: 1,
                mt: 1.75,
                mb: 1.75,
              }}
              gutterBottom
            >
              Files
            </Typography>

            <List>
              {files.map((file, index) => (
                <ListItem key={index}>
                  <ListItemButton onClick={() => handleFileSelect(file)}>
                    <ListItemText primary={file.name} />
                    <ListItemIcon>{file.icon}</ListItemIcon>
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper>
            <CodeMirror
              value={activeFileIndex == 1 ? dependencyValue : codeValue}
              height="500px"
              theme={vscodeDark}
              extensions={python()}
              onChange={onChange}
            />
          </Paper>
        </Grid>
      </Grid>
    </>
  );
});

export default CodeEditor;
