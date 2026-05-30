import React, { useEffect, useRef, useState } from "react";
import "../styles/voiceAssistant.css";

export default function VoiceAssistant() {
  const [isListening, setIsListening] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);

  const recognitionRef = useRef(null);

  // ==============================
  // INIT SPEECH RECOGNITION
  // ==============================
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech Recognition not supported in this browser");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      handleUserInput(text);
    };

    recognitionRef.current = recognition;
  }, []);

  // ==============================
  // START LISTENING
  // ==============================
  const startListening = () => {
    setIsListening(true);
    recognitionRef.current?.start();
  };

  const stopListening = () => {
    setIsListening(false);
    recognitionRef.current?.stop();
  };

  // ==============================
  // SEND MESSAGE
  // ==============================
  const handleUserInput = async (text) => {
    if (!text.trim()) return;

    const newMessages = [
      ...messages,
      { role: "user", content: text },
    ];

    setMessages(newMessages);
    setInput("");

    // ==============================
    // CALL BACKEND (MEMORY MANAGER API)
    // ==============================
    const response = await fetch("http://localhost:8000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
      }),
    });

    const data = await response.json();

    const assistantText = data.response;

    setMessages([
      ...newMessages,
      { role: "assistant", content: assistantText },
    ]);

    speak(assistantText);
  };

  // ==============================
  // TEXT TO SPEECH
  // ==============================
  const speak = (text) => {
    const synth = window.speechSynthesis;

    if (!synth) return;

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);

    synth.speak(utterance);
  };

  return (
    <div className="assistant-container">

      {/* HEADER */}
      <div className="header">
        <h1>🧠 Memory AI Assistant</h1>
        <p>Voice-enabled cognitive memory system</p>
      </div>

      {/* WAVE ANIMATION */}
      <div className="wave-container">
        <div className={`wave ${isListening ? "active" : ""}`}></div>
        <div className={`wave ${isSpeaking ? "active" : ""}`}></div>
        <div className="wave"></div>
      </div>

      {/* CHAT BOX */}
      <div className="chat-box">
        {messages.map((msg, i) => (
          <div key={i} className={`msg ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>

      {/* INPUT AREA */}
      <div className="controls">

        <button
          className={`mic-btn ${isListening ? "on" : ""}`}
          onClick={isListening ? stopListening : startListening}
        >
          🎤
        </button>

        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type or speak..."
        />

        <button
          onClick={() => handleUserInput(input)}
          className="send-btn"
        >
          ➤
        </button>

      </div>
    </div>
  );
}