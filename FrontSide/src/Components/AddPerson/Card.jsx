import React, { useState } from "react";
import "./Card.css";

const Card = ({ showCard, onToggleCard }) => {
  const [name, setName] = useState("");
  const [image, setImage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    onToggleCard(false);
    const formData = new FormData();
    formData.append("name", name);
    formData.append("image", image);
    setImage(null);
    setName("");

    try {
      const response = await fetch("http://localhost:5000/upload-image", {
        method: "POST",
        body: formData,
      });
      if (response.ok) {
        console.log("Image uploaded successfully");
      } else {
        console.error("Image upload failed");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <form
      className={`card-container ${showCard ? "show" : "hide"}`}
      onSubmit={handleSubmit}
    >
      <label className="input-label" htmlFor="name">
        Name To Add
      </label>
      <input
        type="text"
        id="name"
        placeholder="Enter name"
        className="input-name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <label className="input-label" htmlFor="image">
        Image To Upload
      </label>
      <input
        type="file"
        id="image"
        className="input-image"
        onChange={(e) => setImage(e.target.files[0])}
      />
      <button type="submit" className="submit-button">
        Upload
      </button>
    </form>
  );
};

export default Card;
