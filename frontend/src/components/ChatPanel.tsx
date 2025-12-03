import React, { useState, useRef, useEffect } from "react";
import { soundManager } from "../utils/sound";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/cjs/styles/prism";

export type Message = {
  role: "user" | "ai";
  content: string;
  attachments?: string[]; // File paths that were modified
};

type Props = {
  onSendMessage: (message: string, history: Message[]) => Promise<string>;
  selectedFile?: string | null;
  messages: Message[];
  onMessagesChange: (messages: Message[]) => void;
};

// Quick action templates
const QUICK_ACTIONS = [
  { icon: "🚑", label: "Fix bugs", prompt: "Analyze the current file for bugs and fix them" },
  { icon: "✨", label: "Add tests", prompt: "Add unit tests for the current file" },
  { icon: "⚡", label: "Optimize", prompt: "Optimize the current file for better performance" },
  { icon: "📝", label: "Document", prompt: "Add comprehensive documentation and comments to the current file" },
  { icon: "🎨", label: "Refactor", prompt: "Refactor the current file following best practices" },
];

const ChatPanel: React.FC<Props> = ({ onSendMessage, selectedFile, messages, onMessagesChange }) => {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [showActions, setShowActions] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input;
    setInput("");
    setLoading(true);
    soundManager.playClick();
    
    const newHistory = [...messages, { role: "user", content: userMsg } as Message];
    onMessagesChange(newHistory);

    try {
      const response = await onSendMessage(userMsg, newHistory);
      onMessagesChange([...newHistory, { role: "ai", content: response }]);
      soundManager.playMessage();
    } catch (error) {
      onMessagesChange([
        ...newHistory,
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

  const handleQuickAction = async (action: typeof QUICK_ACTIONS[0]) => {
    const contextPrompt = selectedFile 
      ? `${action.prompt} in file: ${selectedFile}`
      : action.prompt;
    setInput(contextPrompt);
    setShowActions(false);
    soundManager.playClick();
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="glass-panel" style={{ display: "flex", flexDirection: "column", height: "100%", borderRadius: "8px", overflow: "hidden" }}>
      {/* Header */}
      <div style={{ 
        padding: "0.75rem 1rem", 
        borderBottom: "1px solid rgba(255,255,255,0.1)",
        background: "rgba(0,0,0,0.3)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center"
      }}>
        <div>
          <div style={{ fontWeight: "bold", color: "#fff", fontSize: "1rem" }}>🤖 AI Assistant</div>
          <div style={{ fontSize: "0.7rem", color: "#9ca3af", marginTop: "2px" }}>
            {selectedFile ? `Context: ${selectedFile}` : "General chat"}
          </div>
        </div>
        <button
          type="button"
          onClick={() => setShowActions(!showActions)}
          title="Quick Actions"
          style={{
            background: "rgba(59, 130, 246, 0.2)",
            color: "#60a5fa",
            border: "1px solid rgba(59, 130, 246, 0.3)",
            padding: "4px 8px",
            borderRadius: "4px",
            fontSize: "0.8rem",
            cursor: "pointer"
          }}
        >
          ⚡ Quick Actions
        </button>
      </div>

      {/* Quick Actions Panel */}
      {showActions && (
        <div style={{ 
          padding: "0.5rem", 
          borderBottom: "1px solid rgba(255,255,255,0.1)",
          background: "rgba(0,0,0,0.2)",
          display: "flex",
          gap: "0.5rem",
          flexWrap: "wrap"
        }}>
          {QUICK_ACTIONS.map((action, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleQuickAction(action)}
              style={{
                background: "rgba(255,255,255,0.05)",
                color: "#d1d5db",
                border: "1px solid rgba(255,255,255,0.1)",
                padding: "4px 10px",
                borderRadius: "12px",
                fontSize: "0.8rem",
                cursor: "pointer",
                transition: "all 0.2s"
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(59, 130, 246, 0.3)";
                e.currentTarget.style.borderColor = "rgba(59, 130, 246, 0.5)";
                soundManager.playHover();
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "rgba(255,255,255,0.05)";
                e.currentTarget.style.borderColor = "rgba(255,255,255,0.1)";
              }}
            >
              {action.icon} {action.label}
            </button>
          ))}
        </div>
      )}

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "1rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
        {messages.length === 0 && (
          <div style={{ 
            color: "#9ca3af", 
            textAlign: "center", 
            marginTop: "3rem",
            fontSize: "0.9rem",
            lineHeight: 1.6
          }}>
            <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>💬</div>
            <div>Start a conversation with AI</div>
            <div style={{ fontSize: "0.8rem", opacity: 0.7, marginTop: "0.5rem" }}>
              Try quick actions or use voice control 🎤
            </div>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              display: "flex",
              flexDirection: "column",
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              maxWidth: "85%",
              gap: "0.25rem"
            }}
          >
            <div style={{ 
              fontSize: "0.7rem", 
              color: "#9ca3af",
              marginLeft: msg.role === "user" ? "auto" : "0.5rem",
              marginRight: msg.role === "user" ? "0.5rem" : "auto"
            }}>
              {msg.role === "user" ? "You" : "AI"}
            </div>
            <div
              className="chat-message"
              style={{
                background: msg.role === "user" 
                  ? "linear-gradient(135deg, rgba(59, 130, 246, 0.9) 0%, rgba(37, 99, 235, 0.9) 100%)" 
                  : "rgba(55, 65, 81, 0.9)",
                backdropFilter: "blur(8px)",
                color: "white",
                padding: "0.75rem 1rem",
                borderRadius: msg.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                fontSize: "0.9rem",
                lineHeight: "1.5",
                boxShadow: "0 4px 6px rgba(0,0,0,0.3)",
                border: `1px solid ${msg.role === "user" ? "rgba(59, 130, 246, 0.3)" : "rgba(255,255,255,0.1)"}`,
              }}
            >
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={vscDarkPlus as any}
                        language={match[1]}
                        PreTag="div"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={className} {...props} style={{ 
                        background: "rgba(0,0,0,0.3)", 
                        padding: "2px 4px", 
                        borderRadius: "3px",
                        fontSize: "0.85em"
                      }}>
                        {children}
                      </code>
                    );
                  }
                }}
              >
                {msg.content}
              </ReactMarkdown>
              
              {/* File attachments */}
              {msg.attachments && msg.attachments.length > 0 && (
                <div style={{ 
                  marginTop: "0.5rem", 
                  paddingTop: "0.5rem", 
                  borderTop: "1px solid rgba(255,255,255,0.2)",
                  fontSize: "0.8rem"
                }}>
                  <div style={{ opacity: 0.7, marginBottom: "0.25rem" }}>Modified files:</div>
                  {msg.attachments.map((file, i) => (
                    <div key={i} style={{ 
                      background: "rgba(0,0,0,0.3)", 
                      padding: "2px 6px", 
                      borderRadius: "3px",
                      display: "inline-block",
                      marginRight: "0.25rem",
                      marginBottom: "0.25rem"
                    }}>
                      📄 {file}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ 
            alignSelf: "flex-start", 
            color: "#60a5fa", 
            fontSize: "0.85rem", 
            marginLeft: "0.5rem",
            display: "flex",
            alignItems: "center",
            gap: "0.5rem"
          }}>
            <div className="typing-indicator">
              <span></span><span></span><span></span>
            </div>
            AI is thinking...
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
      <style jsx global>{`
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
          70% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
          100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
        
        .typing-indicator {
          display: flex;
          gap: 4px;
        }
        
        .typing-indicator span {
          width: 6px;
          height: 6px;
          background: #60a5fa;
          border-radius: 50%;
          animation: typing-bounce 1.4s infinite;
        }
        
        .typing-indicator span:nth-child(2) {
          animation-delay: 0.2s;
        }
        
        .typing-indicator span:nth-child(3) {
          animation-delay: 0.4s;
        }
        
        @keyframes typing-bounce {
          0%, 60%, 100% { transform: translateY(0); opacity: 1; }
          30% { transform: translateY(-8px); opacity: 0.7; }
        }
        
        .chat-message a {
          color: #60a5fa;
          text-decoration: underline;
        }
        
        .chat-message ul, .chat-message ol {
          margin: 0.5rem 0;
          padding-left: 1.5rem;
        }
        
        .chat-message p {
          margin: 0.5rem 0;
        }
        
        .chat-message p:first-child {
          margin-top: 0;
        }
        
        .chat-message p:last-child {
          margin-bottom: 0;
        }
        
        .chat-message pre {
          margin: 0.5rem 0;
          border-radius: 6px;
          overflow-x: auto;
        }
        
        .chat-message blockquote {
          border-left: 3px solid rgba(59, 130, 246, 0.5);
          padding-left: 0.75rem;
          margin: 0.5rem 0;
          opacity: 0.9;
        }
      `}</style>
    </div>
  );
};

export default ChatPanel;
