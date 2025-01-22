import { useState } from "react";
import "./App.css";
import GuestPage from "./Pages/GuestPage/GuestPage";
import { BrowserRouter, Routes, Route } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<GuestPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
