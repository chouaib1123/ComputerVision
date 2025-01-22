import React, { useRef, useEffect, useState } from "react";
import PropTypes from "prop-types";
import "./VideoCapture.css";

const VideoCapture = ({ isConnected, showCard }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 740, height: 480 });
  const [message, setMessage] = useState("Face Processing ...");

  // Setup camera once on mount
  useEffect(() => {
    const setupCamera = async () => {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: dimensions.width },
          height: { ideal: dimensions.height },
        },
      });
      videoRef.current.srcObject = stream;
      await videoRef.current.play();
    };

    if (videoRef.current) {
      setupCamera().catch(console.error);
    }
  }, []);

  // Handle frame capture only when connected
  useEffect(() => {
    let frameInterval = null;

    if (isConnected && videoRef.current && !showCard) {
      frameInterval = setInterval(() => {
        captureFrameAndSend();
      }, 2000);
    }

    return () => {
      if (frameInterval) clearInterval(frameInterval);
    };
  }, [isConnected, showCard]);

  const captureFrameAndSend = async () => {
    if (!canvasRef.current || !videoRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;

    canvas.width = dimensions.width;
    canvas.height = dimensions.height;

    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    setMessage("Face Processing ...");
    try {
      const response = await fetch("http://localhost:5000/process-frame", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          frame: canvas.toDataURL("image/png"),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setMessage(data.message);
      console.log("Response from server:", data);
    } catch (error) {
      console.error("Error sending frame:", error);
    }
  };

  return (
    <div className="video-container">
      <video
        ref={videoRef}
        width={dimensions.width}
        height={dimensions.height}
        autoPlay
        playsInline
        muted
      />
      <canvas
        ref={canvasRef}
        width={dimensions.width}
        height={dimensions.height}
        style={{ display: "none" }}
      />
      {isConnected && <p>{message}</p>}
    </div>
  );
};

VideoCapture.propTypes = {
  isConnected: PropTypes.bool.isRequired,
  showCard: PropTypes.bool.isRequired,
};

export default VideoCapture;
