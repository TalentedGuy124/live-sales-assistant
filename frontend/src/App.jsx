// App.jsx (Final Version)

import React, { useState, useEffect } from 'react';
// We have removed the 'import WebSocket...' line completely!
import './App.css'; 

function App() {
  const [suggestions, setSuggestions] = useState([]);
  const [status, setStatus] = useState('Connecting to Assistant...');

  useEffect(() => {
    // This line now uses the WebSocket that is BUILT-IN to your browser.
    const socket = new WebSocket('ws://localhost:8765');

    socket.onopen = () => {
      setStatus('Connected. Waiting for suggestions...');
      console.log('Connected to WebSocket server!');
    };

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log('Received data:', message);
        
        if (message.ranked_suggestions) {
          setStatus(`Received ${message.ranked_suggestions.length} suggestion(s).`);
          setSuggestions(message.ranked_suggestions);
        }
      } catch (error) {
        console.error('Error parsing data:', error);
      }
    };

    socket.onclose = () => {
      setStatus('Disconnected from Assistant.');
      console.log('WebSocket connection closed.');
    };

    socket.onerror = (err) => {
      setStatus('Connection Error.');
      console.error('WebSocket error:', err);
    };

    return () => {
      socket.close();
    };
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Live Sales Assistant</h1>
        <p className="status">{status}</p>
      </header>
      <main className="App-main">
        <h2>Talking Points</h2>
        <div className="suggestions-list">
          {suggestions.length > 0 ? (
            suggestions.map((suggestion, index) => (
              <div key={index} className="suggestion-card">
                <p className="point">{suggestion.point}</p>
                <div className="provenance">
                  <span className="confidence" style={{backgroundColor: suggestion.confidence > 0.85 ? '#2E7D32' : '#FFAB00'}}>
                    Confidence: {Math.round(suggestion.confidence * 100)}%
                  </span>
                  <span className="sources">
                    Sources: {suggestion.sources.join(', ')}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <p className="no-suggestions">No suggestions yet. Start the backend test to see results.</p>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;