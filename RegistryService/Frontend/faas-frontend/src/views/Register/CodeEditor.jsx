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
const CodeEditor = forwardRef((props, ref) => {
  const [value, setValue] = useState("print('Hello World!')");
  const [files, setFiles] = useState([
    { name: "app.py", content: value, icon: <CodeIcon /> },
    { name: "requirements.txt", content: "", icon: <TextSnippetIcon /> },
  ]);
  const [activeFileIndex, setActiveFileIndex] = useState(0);
  const dispatch = useDispatch();
  const handleSubmit = () => {
    handleFileContentChange(activeFileIndex, value);
    dispatch({
      type: SAVE_CODE_DEPS,
      ...{ code: files[0].content, deps: files[1].content, runtime: "python" },
    });
  };
  useImperativeHandle(ref, () => {
    return {
      handleSubmit,
    };
  });
  const handleFileSelect = (file) => {
    const index = files.findIndex((f) => f.name === file.name);
    if (index != activeFileIndex) {
      setActiveFileIndex(index);
      handleFileContentChange((index + 1) % 2, value);
      setValue(file.content);
    }
  };
  const handleFileContentChange = (index, content) => {
    const updatedFiles = [...files];
    updatedFiles[index].content = content;
    setFiles(updatedFiles);
    console.log("Handled content change for index ", index);
    console.log("New content:", content);
  };
  const onChange = React.useCallback((val, viewUpdate) => {
    console.log(val);
    setValue(val);
  }, []);
  useEffect(() => {
    console.log("Initially:");
    console.log(files);
  }, []);
  return (
    <>
      <Grid container>
        <Grid item sx={{ width: "30%", mt: 1.75, mb: 1 }}>
          <TextField
            disabled
            id="runtime-select"
            select
            label="Runtime Type"
            defaultValue="Python"
            fullWidth
          >
            <MenuItem key={"runtime"} value={"Python"}>
              Python
            </MenuItem>
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
              value={value}
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
