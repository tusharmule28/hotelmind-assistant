"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, MapPin, Star, IndianRupee, Loader2 } from "lucide-react";
import styles from "./page.module.css";

const MOCK_USER_ID = "user_123_frontend";

export default function Home() {
  const [messages, setMessages] = useState([
    {
      role: "ai",
      content: "Hello! I am your AI Hotel Assistant. How can I help you find the perfect stay today?",
      id: "init",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: "user", content: input, id: crypto.randomUUID() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Connect to FastAPI backend
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage.content, user_id: MOCK_USER_ID }),
      });

      if (!response.ok) throw new Error("API failed");
      const data = await response.json();

      const aiMessage = {
        role: "ai",
        content: data.reply,
        results: data.results,
        booking: data.booking,
        hitl_ticket_id: data.hitl_ticket_id,
        id: crypto.randomUUID(),
      };
      
      // Simulate streaming response on the frontend by updating progressively
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { role: "ai", content: "Sorry, I am having trouble connecting to the server.", id: crypto.randomUUID() },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.chatContainer}>
      <header className={styles.header}>
        <div className={styles.logoGroup}>
          <div className={styles.logoPulse}></div>
          <h1>HotelBookingAI</h1>
        </div>
        <p>Premium AI Assistant</p>
      </header>

      <main className={styles.chatWindow}>
        <div className={styles.messageList}>
          <AnimatePresence>
            {messages.map((msg, idx) => (
              <motion.div
                key={msg.id || idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className={msg.role === "user" ? styles.userMessageWrapper : styles.aiMessageWrapper}
              >
                <div className={msg.role === "user" ? styles.userMessage : styles.aiMessage}>
                  {msg.role === "ai" && <TypewriterText text={msg.content} />}
                  {msg.role === "user" && <p>{msg.content}</p>}
                </div>
                
                {/* Render Hotel Search Results */}
                {msg.results && msg.results.length > 0 && (
                  <motion.div 
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.5 }}
                    className={styles.hotelGrid}
                  >
                    {msg.results.map((hotel, idx) => (
                      <div key={hotel.id || `hotel-${idx}`} className={styles.hotelCard}>
                        <div className={styles.hotelImagePlaceholder}>
                          <img src={`https://source.unsplash.com/random/400x300/?hotel,${hotel.location}`} alt="Hotel" />
                          <div className={styles.priceTag}>₹{hotel.price_per_night}/night</div>
                        </div>
                        <div className={styles.hotelInfo}>
                          <h3>{hotel.name}</h3>
                          <div className={styles.hotelMeta}>
                            <span className={styles.location}><MapPin size={14}/> {hotel.location}</span>
                            <span className={styles.rating}><Star size={14}/> {hotel.rating}/5</span>
                          </div>
                          <p className={styles.hotelExplanation}>{hotel.explanation}</p>
                          {hotel.amenities && hotel.amenities.length > 0 && (
                            <div className={styles.amenities}>
                              {hotel.amenities.slice(0, 3).map((a, i) => (
                                <span key={i} className={styles.amenityTag}>{a}</span>
                              ))}
                            </div>
                          )}
                          <button className={styles.bookBtn} onClick={() => setInput(`Book a room at ${hotel.name}`)}>
                            Book Now
                          </button>
                        </div>
                      </div>
                    ))}
                  </motion.div>
                )}

                {/* Render Booking Confirmation */}
                {msg.booking && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={styles.bookingCard}
                  >
                    <h3>Booking Held!</h3>
                    <p>Booking ID: <strong>{msg.booking.booking_id}</strong></p>
                    <p>Expires in: 15 minutes</p>
                    <button className={styles.confirmBtn} onClick={() => setInput(`Confirm booking ${msg.booking.booking_id}`)}>
                      Confirm Reservation
                    </button>
                  </motion.div>
                )}
              </motion.div>
            ))}
            {isLoading && (
              <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className={styles.aiMessageWrapper}>
                <div className={styles.loadingBubble}>
                  <Loader2 className={styles.spinner} size={20} />
                  <span>AI is thinking...</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>
      </main>

      <form onSubmit={handleSend} className={styles.inputArea}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask for hotels in Pune under ₹3000..."
          disabled={isLoading}
          className={styles.textInput}
        />
        <button type="submit" disabled={!input.trim() || isLoading} className={styles.sendBtn}>
          <Send size={20} />
        </button>
      </form>
    </div>
  );
}

// Simple Typewriter effect component for text
function TypewriterText({ text }) {
  const [displayed, setDisplayed] = useState("");

  useEffect(() => {
    let i = 0;
    setDisplayed("");
    const interval = setInterval(() => {
      setDisplayed((prev) => prev + (text.charAt(i) || ""));
      i++;
      if (i >= text.length) clearInterval(interval);
    }, 15); // streaming speed
    return () => clearInterval(interval);
  }, [text]);

  return <p>{displayed}</p>;
}
