import { lazy } from "react";

// project imports
import MainLayout from "../layout/MainLayout";
import Loadable from "../ui-component/Loadable";
import { element } from "prop-types";
// dashboard routing
const DashboardDefault = Loadable(
  lazy(() => import("../views/dashboard/Default"))
);
const RegisterFunction = Loadable(
  lazy(() => import("../views/Register/FunctionRegistry"))
);
const S4 = Loadable(lazy(() => import("../views/S4/S4Service")));
const Status = Loadable(lazy(() => import("../views/Status/StatusPage")));

// ==============================|| MAIN ROUTING ||============================== //

const MainRoutes = {
  path: "/",
  element: <MainLayout />,
  children: [
    {
      path: "/",
      element: <DashboardDefault />,
    },
    {
      path: "/register",
      element: <RegisterFunction />,
    },
    {
      path: "/s4",
      element: <S4 />,
    },
    {
      path: "/status",
      element: <Status />,
    },
  ],
};

export default MainRoutes;
