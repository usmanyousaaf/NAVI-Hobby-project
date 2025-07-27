// nextjs-frontend/pages/_app.tsx
import type { AppProps } from "next/app";
import Image from "next/image";  // Import Next.js Image component

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <style jsx global>{`
        * {
          box-sizing: border-box;
          margin: 0;
          padding: 0;
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }
        body {
          background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e0 100%);
          min-height: 100vh;
          color: #1a202c;
          overflow-x: hidden;
          position: relative;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulseTitle {
          0% { transform: scale(1); }
          50% { transform: scale(1.01); }
          100% { transform: scale(1); }
        }

        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        .navbar-logo {
          display: flex;
          align-items: center;
          gap: 0.8rem;
        }
        .navbar-title {
            font-size: 1.8rem;
            font-weight: 900;
            background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: pulseTitle 4s infinite;
        }

        .app-container {
          display: flex;
          min-height: 100vh;
          padding: 6rem 2rem 2rem 2rem;
          position: relative;
        }
        .chat-sidebar {
          flex: 1;
          padding: 2rem;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: flex-start;
        }
        .sidebar-title {
          font-size: 2.8rem;
          font-weight: 900;
          background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          margin-bottom: 1.2rem;
        }
        .sidebar-subtitle {
          font-size: 1.3rem;
          color: #2d3748;
          font-weight: 700;
          margin-bottom: 2rem;
          max-width: 500px;
        }
        .sidebar-description {
            font-size: 1.1rem;
            color: #4a5568;
            font-weight: 600;
            margin-bottom: 2rem;
            max-width: 550px;
            line-height: 1.6;
        }
        .hobby-list {
          list-style: none;
          margin-top: 2rem;
        }
        .hobby-list li {
          margin-bottom: 1.2rem;
          position: relative;
          padding-left: 1.8rem;
          font-size: 1.15rem;
          font-weight: 700;
          color: #2d3748;
        }
        .hobby-list li:before {
          content: "▶";
          position: absolute;
          left: 0;
          color: #4a5568;
          font-size: 1rem;
          line-height: 1;
        }
        .chat-container {
          display: flex;
          flex-direction: column;
          height: 85vh;
          width: 450px;
          background: white;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
          border-radius: 20px;
          overflow: hidden;
          border: 1px solid rgba(0,0,0,0.05);
        }
        .chat-header {
          background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
          color: white;
          padding: 1.3rem 1.5rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        }
        .chat-header h2 {
          font-weight: 600;
          font-size: 1.4rem;
        }
        .restart-btn {
          background: rgba(255, 255, 255, 0.2);
          border: none;
          color: white;
          padding: 0.6rem 1.2rem;
          border-radius: 25px;
          cursor: pointer;
          font-size: 0.95rem;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          gap: 0.6rem;
        }
        .restart-btn:hover {
          background: rgba(255, 255, 255, 0.3);
        }
        .messages {
          flex: 1;
          padding: 1.5rem;
          overflow-y: auto;
          background: #f8fafc;
          display: flex;
          flex-direction: column;
          gap: 1.2rem;
        }
        .message {
          display: flex;
          animation: fadeIn 0.4s ease-out;
        }
        .message.user {
          justify-content: flex-end;
        }
        .message.bot {
          justify-content: flex-start;
        }
        .bubble {
          max-width: 80%;
          padding: 1rem 1.4rem;
          border-radius: 20px;
          position: relative;
          word-wrap: break-word;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
          line-height: 1.5;
          font-weight: 500;
        }
        .user .bubble {
          background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
          color: white;
          border-bottom-right-radius: 6px;
        }
        .bot .bubble {
          background: white;
          color: #2d3748;
          border-bottom-left-radius: 6px;
          border: 1px solid #e2e8f0;
        }
        .timestamp {
          font-size: 0.75rem;
          opacity: 0.85;
          margin-top: 0.4rem;
          text-align: right;
        }
        .user .timestamp {
          color: rgba(255, 255, 255, 0.85);
        }
        .bot .timestamp {
          color: rgba(45, 55, 72, 0.7);
        }
        .input-area {
          display: flex;
          padding: 1.2rem;
          background: white;
          border-top: 1px solid #edf2f7;
        }
        .input-area input {
          flex: 1;
          padding: 0.9rem 1.3rem;
          border: 1px solid #e2e8f0;
          border-radius: 2rem;
          outline: none;
          font-size: 1.05rem;
          transition: all 0.2s;
          font-weight: 500;
        }
        .input-area input:focus {
          border-color: #4a5568;
          box-shadow: 0 0 0 3px rgba(74, 85, 104, 0.2);
        }
        .input-area input:disabled {
          background: #f1f5f9;
          cursor: not-allowed;
        }
        .input-area button {
          width: 50px;
          height: 50px;
          margin-left: 0.9rem;
          border: none;
          background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
          color: white;
          border-radius: 50%;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }
        .input-area button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(45, 55, 72, 0.3);
        }
        .input-area button:disabled {
          background: #a0aec0;
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }
        .input-area button svg {
          width: 22px;
          height: 22px;
        }
        .typing-indicator {
          display: flex;
          padding: 0.6rem 0;
          align-items: center;
        }
        .typing-indicator span {
          height: 9px;
          width: 9px;
          background: #4a5568;
          border-radius: 50%;
          display: inline-block;
          margin: 0 3px;
          animation: typing 1.2s infinite ease-in-out;
        }
        @keyframes typing {
          0% { opacity: 0.4; }
          50% { opacity: 1; }
          100% { opacity: 0.4; }
        }
        .typing-indicator span:nth-child(2) {
          animation-delay: 0.2s;
        }
        .typing-indicator span:nth-child(3) {
          animation-delay: 0.4s;
        }

        @media (max-width: 768px) {
          .navbar {
            padding: 0.8rem 1rem;
          }
          .navbar-title {
            font-size: 1.5rem;
          }
          .app-container {
            flex-direction: column;
            padding: 5rem 1rem 1rem 1rem;
          }
          .chat-sidebar {
            padding: 1.5rem 1rem;
            align-items: center;
            text-align: center;
          }
           .sidebar-title {
              font-size: 2.2rem;
            }
            .sidebar-subtitle {
              font-size: 1.1rem;
            }
            .sidebar-description {
                font-size: 1rem;
            }
            .hobby-list li {
                font-size: 1rem;
            }
          .chat-container {
            width: 100%;
            height: 75vh;
            border-radius: 16px;
          }
          .bubble {
            max-width: 88%;
            padding: 0.8rem 1.1rem;
          }
          .chat-header h2 {
            font-size: 1.2rem;
          }
          .input-area {
            padding: 0.9rem;
          }
          .input-area input {
            padding: 0.7rem 1rem;
            font-size: 0.95rem;
          }
          .input-area button {
            width: 44px;
            height: 44px;
            margin-left: 0.7rem;
          }
        }
      `}</style>

      <nav className="navbar">
        <div className="navbar-logo">
          <Image src="/logo.png" alt="NAVI Hobby Logo" width={40} height={40} />
          <div className="navbar-title">NAVI Hobby</div>
        </div>
      </nav>

      <div className="app-container">
        <div className="chat-sidebar">
          <h1 className="sidebar-title">
            Find Hobbies That Match Your Lifestyle and Personality
          </h1>
          <p className="sidebar-subtitle">
            Welcome to NAVI Hobby – the ultimate destination for hobby discovery!
          </p>
          <p className="sidebar-description">
            Our intelligent platform uses your preferences, available time, budget, and skill level to recommend hobbies that truly resonate with you. From photography and cooking to woodworking and astronomy, we make it easy to explore hundreds of activities through detailed guides, community reviews, and local group connections. Stop wondering what to do with your free time – start discovering hobbies that bring you joy and fulfillment.
          </p>
          <ul className="hobby-list">
            <li>Creative Coding & Generative Art</li>
            <li>Craft Cocktail Mastery</li>
            <li>DIY Electronics & Arduino Projects</li>
            <li>Conversational Language Fluency</li>
            <li>Urban Gardening & Hydroponics</li>
            <li>Strategic Board Gaming</li>
          </ul>
        </div>
        <Component {...pageProps} />
      </div>
    </>
  );
}
