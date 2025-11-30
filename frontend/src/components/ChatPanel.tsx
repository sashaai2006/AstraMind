import React, { useState, useRef, useEffect } from "react";
import { soundManager } from "../utils/sound";

export type Message = {
  role: "user" | "ai";
  content: string;
};

type Props = {
  onSendMessage: (message: string, history: Message[]) => Promise<string>;
};

const ChatPanel: React.FC<Props> = ({ onSendMessage }) => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input;
    setInput("");
    setLoading(true);
    soundManager.playClick();
    
    const newHistory = [...messages, { role: "user", content: userMsg } as Message];
    setMessages(newHistory);

    try {
      const response = await onSendMessage(userMsg, newHistory);
      setMessages((prev) => [...prev, { role: "ai", content: response }]);
      soundManager.playMessage();
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "ai", content: `Error: ${(error as Error).message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const toggleListening = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Voice control not supported in this browser.");
      return;
    }

    if (listening) {
      // Stop handled by onend
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setListening(true);
      soundManager.playHover(); // Feedback start
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInput((prev) => (prev ? prev + " " + transcript : transcript));
    };

    recognition.onerror = (event: any) => {
      console.error("Speech recognition error", event.error);
      setListening(false);
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognition.start();
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="glass-panel" style={{ display: "flex", flexDirection: "column", height: "100%", borderRadius: "8px", overflow: "hidden" }}>
      <div style={{ flex: 1, overflowY: "auto", padding: "1rem", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {messages.length === 0 && (
          <div style={{ color: "#9ca3af", textAlign: "center", marginTop: "2rem" }}>
            Ask me to refactor code, create files, or explain logic.<br/>
            <span style={{ fontSize: "0.8rem", opacity: 0.7 }}>(Try voice control!)</span>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              background: msg.role === "user" ? "rgba(59, 130, 246, 0.8)" : "rgba(55, 65, 81, 0.8)",
              backdropFilter: "blur(4px)",
              color: "white",
              padding: "0.5rem 0.75rem",
              borderRadius: "8px",
              maxWidth: "85%",
              fontSize: "0.9rem",
              lineHeight: "1.4",
              whiteSpace: "pre-wrap",
              boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
              border: "1px solid rgba(255,255,255,0.1)"
            }}
          >
            {msg.content}
          </div>
        ))}
        {loading && (
          <div style={{ alignSelf: "flex-start", color: "#60a5fa", fontSize: "0.8rem", marginLeft: "0.5rem" }}>
            Thinking & coding...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form
        onSubmit={handleSend}
        style={{
          padding: "0.75rem",
          borderTop: "1px solid rgba(255,255,255,0.1)",
          display: "flex",
          gap: "0.5rem",
          background: "rgba(0,0,0,0.2)",
        }}
      >
        <button
          type="button"
          onClick={toggleListening}
          title="Voice Control"
          style={{
            background: listening ? "#ef4444" : "rgba(255,255,255,0.1)",
            color: "white",
            border: "1px solid rgba(255,255,255,0.1)",
            width: "36px",
            borderRadius: "4px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            animation: listening ? "pulse 1.5s infinite" : "none"
          }}
        >
          {listening ? "●" : "🎤"}
        </button>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Message AI..."
          disabled={loading}
          style={{
            flex: 1,
            background: "rgba(0,0,0,0.3)",
            border: "1px solid rgba(255,255,255,0.2)",
            color: "white",
            padding: "0.5rem",
            borderRadius: "4px",
            fontSize: "0.9rem",
          }}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          onMouseEnter={() => !loading && soundManager.playHover()}
          style={{
            background: loading ? "rgba(75, 85, 99, 0.5)" : "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
            color: "white",
            border: "none",
            padding: "0 1rem",
            borderRadius: "4px",
            cursor: loading ? "not-allowed" : "pointer",
            fontWeight: "bold",
          }}
        >
          Send
        </button>
      </form>
      <style jsx>{`
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
          70% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
          100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
      `}</style>
    </div>
  );
};

export default ChatPanel;
