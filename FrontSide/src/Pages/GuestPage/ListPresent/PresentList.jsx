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

const TIME_RANGES = ["8:00-10:00", "10:00-12:00", "14:00-16:00", "16:00-19:00"];

const TIME_RANGE_MAP = {
  "8:00-10:00": "TimeRange.RANGE_8_10",
  "10:00-12:00": "TimeRange.RANGE_10_12",
  "14:00-16:00": "TimeRange.RANGE_14_16",
  "16:00-19:00": "TimeRange.RANGE_16_19",
};

const PresentList = ({ isConnected, setIsConnected }) => {
  const [persons, setPersons] = useState([]);

  const formattedDate = useMemo(() => {
    const today = new Date();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const date = String(today.getDate()).padStart(2, "0");
    const year = today.getFullYear();
    return `${month}/${date}/${year}`;
  }, []);

  const formatTime = (time) => {
    if (!time) return "-";
    return time.substring(0, 5); // HH:mm format
  };

  const fetchPersons = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/get-all-persons");
      const data = await response.json();
      console.log("Persons data:", data);
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
              {TIME_RANGES.map((range) => (
                <div className="table-cell" key={range}>
                  {range}
                </div>
              ))}
            </div>
          </div>
          <div className="table-body">
            {persons.map((person) => (
              <div className="table-row" key={person.id}>
                <div className="table-cell">{person.name}</div>
                {TIME_RANGES.map((range) => (
                  <div className="table-cell" key={`${person.id}-${range}`}>
                    {person.presences[TIME_RANGE_MAP[range]] ? (
                      <div className="presence-status present">Present</div>
                    ) : (
                      <div className="presence-status absent">-</div>
                    )}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PresentList;
