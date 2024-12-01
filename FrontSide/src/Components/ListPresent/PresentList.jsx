import React, { useEffect, useState, useMemo } from "react";
import io from "socket.io-client";
import "./PresentList.css";

const socket = io("http://localhost:5000", {
  transports: ["websocket", "polling"],
  withCredentials: true,
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionAttempts: 1000,
});

const PresentList = ({ isConnected, setIsConnected }) => {
  const [persons, setPersons] = useState([]);

  const formattedDate = useMemo(() => {
    const today = new Date();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const date = String(today.getDate()).padStart(2, "0");
    const year = today.getFullYear();
    return `${month}/${date}/${year}`;
  }, []);

  // New helper function for time formatting
  const formatPresenceTime = (isoString) => {
    if (!isoString) return "Not present";
    const date = new Date(isoString);
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");
    return `${hours}:${minutes}:${seconds}`;
  };

  const fetchPersons = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/get-all-persons");
      const data = await response.json();
      setPersons(data);
    } catch (error) {
      console.error("Error fetching persons:", error);
    }
  };

  useEffect(() => {
    socket.on("connect", () => {
      setIsConnected(true);
      fetchPersons();
    });

    socket.on("disconnect", () => {
      setIsConnected(false);
      setPersons([]);
    });

    socket.on("persons_data", (data) => {
      setPersons(data);
    });

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("persons_data");
    };
  }, [setIsConnected]);

  return (
    <div className="List">
      <h2>Present List {formattedDate}</h2>

      {!isConnected ? (
        <div className="connection-warning">
          Connecting to server... Please wait
        </div>
      ) : persons.length === 0 ? (
        <div className="empty-message">No persons data available</div>
      ) : (
        <div className="table">
          <div className="table-header">
            <div className="table-row">
              <div className="table-cell">Name</div>
              <div className="table-cell">Presence Status</div>
              <div className="table-cell">Time</div>
            </div>
          </div>
          <div className="table-body">
            {persons.map((person) => (
              <div className="table-row" key={person.id}>
                <div className="table-cell">{person.name}</div>
                <div className="table-cell">
                  {person.presence_datetime ? "Present" : "Absent"}
                </div>
                <div className="table-cell">
                  {person.presence_datetime
                    ? formatPresenceTime(person.presence_datetime)
                    : "-"}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PresentList;
