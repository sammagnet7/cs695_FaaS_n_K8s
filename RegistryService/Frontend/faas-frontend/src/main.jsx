import App from "./App.jsx";
import { createRoot } from "react-dom/client";
import { store } from "./store";
// third party
import { BrowserRouter } from "react-router-dom";
import { Provider } from "react-redux";

// style + assets
import "./assets/scss/style.scss";
import config from "./config.js";
import { SnackbarProvider } from "notistack";

const root = createRoot(document.getElementById("root")).render(
  <Provider store={store}>
    <BrowserRouter basename={config.basename}>
      <SnackbarProvider
        maxSnack={2}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "center",
        }}
      >
        <App />
      </SnackbarProvider>
    </BrowserRouter>
  </Provider>
);
