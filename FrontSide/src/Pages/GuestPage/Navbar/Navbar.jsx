import React, { useState } from "react";
import "./Navbar.css";

const Navbar = ({ showCard, onToggleCard }) => {
  const handleButtonClick = () => {
    onToggleCard(!showCard);
  };

  return (
    <div className="navbar">
      <div className="navbar-title">Today's Presence</div>
      <button onClick={handleButtonClick} className="navbar-button">
        {showCard ? "Adding Person to Database ..." : "Add Person To Database"}
      </button>
    </div>
  );
};

export default Navbar;
