import { useState } from "react";
import VideoCapture from "./VideoSection/VideoCapture";
import PresentList from "./ListPresent/PresentList";
import Navbar from "./Navbar/Navbar";
import Card from "./Card/Card";

function GuestPage() {
  const [showCard, setShowCard] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  return (
    <div className="GuestPage">
      <Navbar showCard={showCard} onToggleCard={setShowCard} />
      <Card showCard={showCard} onToggleCard={setShowCard} />
      <div className="Hidder"></div>
      <div className="TheTwoFriends">
        <PresentList
          isConnected={isConnected}
          setIsConnected={setIsConnected}
        />
        <VideoCapture isConnected={isConnected} showCard={showCard} />
      </div>
    </div>
  );
}

export default GuestPage;
