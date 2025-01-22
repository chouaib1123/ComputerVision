import React, { useRef, useState, useEffect } from "react";
import "./Card.css";

const Card = ({ showCard, onToggleCard }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [name, setName] = useState("");
  const [image, setImage] = useState(null);
  const [isFrozen, setIsFrozen] = useState(false);

  useEffect(() => {
    startVideo();
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const startVideo = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
    } catch (err) {
      console.error("Error accessing camera:", err);
    }
  };

  const takeScreenshot = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);

    video.pause();
    setIsFrozen(true);

    canvas.toBlob((blob) => {
      setImage(blob);
    }, "image/jpeg");
  };

  const resumeVideo = () => {
    const video = videoRef.current;
    video.play();
    setIsFrozen(false);
    setImage(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image || !name.trim()) return;

    const sanitizedName = name
      .trim()
      .replace(/[^a-z0-9]/gi, "_")
      .toLowerCase();
    const filename = `${sanitizedName}.jpg`;

    const formData = new FormData();
    formData.append("name", name);
    formData.append("image", image, filename);

    try {
      const response = await fetch("http://localhost:5000/upload-image", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Upload failed");
      }

      // Reset form on success
      setName("");
      resumeVideo();
      onToggleCard(); // Close the card
    } catch (error) {
      console.error("Upload error:", error);
      alert(error.message);
    }
  };

  return (
    <form
      className={`card-container ${showCard ? "show" : "hide"}`}
      onSubmit={handleSubmit}
    >
      <label className="input-label" htmlFor="name">
        Name
      </label>
      <input
        type="text"
        id="name"
        className="input-text"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />

      <div className="video-container">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          style={{ width: "100%", maxWidth: "500px" }}
        />
        <canvas ref={canvasRef} style={{ display: "none" }} />
      </div>

      {!isFrozen ? (
        <button
          type="button"
          onClick={takeScreenshot}
          className="capture-button"
        >
          Take Screenshot
        </button>
      ) : (
        <button type="button" onClick={resumeVideo} className="capture-button">
          Retake
        </button>
      )}

      <button type="submit" className="submit-button" disabled={!image}>
        Upload
      </button>
    </form>
  );
};

export default Card;
