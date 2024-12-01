import { useState } from "react";
import "./App.css";
import VideoCapture from "./Components/VideoSection/VideoCapture";
import Navbar from "./Components/Navbar/Navbar";
import Card from "./Components/AddPerson/Card";
import PresentList from "./Components/ListPresent/PresentList";

function App() {
  const [showCard, setShowCard] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  return (
    <div className="App">
      <Navbar showCard={showCard} onToggleCard={setShowCard} />
      <Card showCard={showCard} onToggleCard={setShowCard} />
      <div className="Hidder"></div>
      <div className="TheTwoFriends">
        <PresentList
          isConnected={isConnected}
          setIsConnected={setIsConnected}
        />
        <VideoCapture isConnected={isConnected} />
      </div>
    </div>
  );
}

export default App;
