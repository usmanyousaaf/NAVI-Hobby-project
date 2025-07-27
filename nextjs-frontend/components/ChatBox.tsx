// nextjs-frontend/components/ChatBox.tsx
import { useState, useRef, useEffect } from "react";

type Message = {
  sender: "user" | "bot";
  text: string;
  timestamp: Date;
};

export default function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const userIdRef = useRef(Math.random().toString(36).slice(2));
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom and typing animation effect
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // Initial greeting
  useEffect(() => {
    setTimeout(() => {
      setMessages([{
        sender: "bot",
        text: "Hello! I'm your AI assistant. How can I help you today?",
        timestamp: new Date()
      }]);
    }, 500);
  }, []);

  const fetchMessage = async (text: string) => {
    setIsTyping(true);
    try {
      // Simulate network delay for realistic typing effect
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userIdRef.current, message: text }),
      });
      const data = await res.json();
      
      setMessages(prev => [...prev, {
        sender: "bot",
        text: data.text,
        timestamp: new Date()
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        sender: "bot",
        text: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date()
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;
    const text = input.trim();
    const userMessage = {
      sender: "user" as const,
      text,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    await fetchMessage(text);
  };

  const restartConversation = () => {
    setMessages([]);
    setInput("");
    setTimeout(() => {
      setMessages([{
        sender: "bot",
        text: "Hello again! What would you like to talk about this time?",
        timestamp: new Date()
      }]);
    }, 500);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>AI Assistant</h2>
        <button onClick={restartConversation} className="restart-btn">
          New Chat
        </button>
      </div>
      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.sender}`}>
            <div className="bubble">
              <div className="text">{m.text}</div>
              <div className="timestamp">{formatTime(m.timestamp)}</div>
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="message bot">
            <div className="bubble">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-area">
        <input
          type="text"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={isTyping}
        />
        <button onClick={handleSend} disabled={isTyping || !input.trim()}>
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
          </svg>
        </button>
      </div>
    </div>
  );
}