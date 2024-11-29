import "./App.css";
import Main from "./components/Main";
import { FC, ReactElement } from "react";
import React from "react";

const App: FC = (): ReactElement => {
  return (
    <div
      className="App mx-auto"
      style={{ height: "90vh", width: "100vw", minWidth: "400px" }}
    >
      <Main />
    </div>
  );
};

export default App;
