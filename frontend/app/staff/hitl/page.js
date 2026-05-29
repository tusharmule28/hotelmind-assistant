"use client";

import { useEffect, useState } from "react";

export default function HitlDashboard() {
  const [tickets, setTickets] = useState([]);
  const [editingTicket, setEditingTicket] = useState(null);
  const [editDraft, setEditDraft] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch initial tickets
    const fetchTickets = async () => {
      try {
        const res = await fetch("http://localhost:8000/hitl/tickets");
        const data = await res.json();
        setTickets(data);
      } catch (error) {
        console.error("Failed to fetch tickets:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchTickets();

    // Connect to WebSocket
    const ws = new WebSocket("ws://localhost:8000/hitl/ws");
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      if (message.type === "NEW_TICKET") {
        setTickets((prev) => [message.data, ...prev]);
      } else if (message.type === "TICKET_RESOLVED") {
        setTickets((prev) => 
          prev.map((t) => 
            t.id === message.data.ticket_id ? { ...t, status: message.data.status } : t
          )
        );
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  const handleResolve = async (ticketId, action) => {
    try {
      const res = await fetch("http://localhost:8000/hitl/resolve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ticket_id: ticketId,
          action: action,
          new_draft: action === "EDIT" ? editDraft : null,
        }),
      });
      
      if (res.ok) {
        if (action === "EDIT") {
          setEditingTicket(null);
        }
      }
    } catch (error) {
      console.error("Failed to resolve ticket:", error);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div>Loading Tickets...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1>Human-in-the-Loop Review</h1>
        <p>Review AI-generated responses and high-risk actions before they reach the guest.</p>
      </div>

      <div className="ticket-grid">
        {tickets.map((ticket) => (
          <div key={ticket.id} className="glass-card">
            <div className="ticket-header">
              <span className={`badge badge-${
                ticket.severity === "HIGH" ? "danger" : 
                ticket.severity === "MEDIUM" ? "warning" : "success"
              }`}>
                {ticket.trigger_type.replace(/_/g, " ")}
              </span>
              <span className={`badge badge-${
                ticket.status === "PENDING" ? "warning" : 
                ticket.status === "REJECTED" ? "danger" : "success"
              }`}>
                {ticket.status}
              </span>
            </div>
            
            <div className="ticket-body">
              <div className="ticket-meta">
                <span><strong>Confidence:</strong> {(ticket.confidence_score * 100).toFixed(1)}%</span>
                <span><strong>Booking Amount:</strong> ₹{ticket.booking_amount || 0}</span>
                <span><strong>Fraud Score:</strong> {ticket.fraud_score || 0}</span>
              </div>

              {editingTicket === ticket.id ? (
                <div>
                  <textarea 
                    className="textarea-edit" 
                    value={editDraft} 
                    onChange={(e) => setEditDraft(e.target.value)}
                  />
                  <div className="ticket-actions">
                    <button className="btn btn-primary" onClick={() => handleResolve(ticket.id, "EDIT")}>Save Edit</button>
                    <button className="btn btn-secondary" onClick={() => setEditingTicket(null)}>Cancel</button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="ticket-draft">
                    {ticket.ai_draft}
                  </div>
                  
                  {ticket.status === "PENDING" && (
                    <div className="ticket-actions">
                      <button className="btn btn-success" onClick={() => handleResolve(ticket.id, "APPROVE")}>Approve</button>
                      <button className="btn btn-secondary" onClick={() => {
                        setEditingTicket(ticket.id);
                        setEditDraft(ticket.ai_draft);
                      }}>Edit</button>
                      <button className="btn btn-danger" onClick={() => handleResolve(ticket.id, "REJECT")}>Reject</button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        ))}
        
        {tickets.length === 0 && (
          <div style={{ color: "var(--text-secondary)" }}>
            No pending tickets found.
          </div>
        )}
      </div>
    </div>
  );
}
