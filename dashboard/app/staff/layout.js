export const metadata = {
  title: "Hotel AI - Staff Dashboard",
  description: "Human-in-the-Loop Management Dashboard",
};

export default function StaffLayout({ children }) {
  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <h2>Hotel AI Dashboard</h2>
        <nav>
          <a href="/staff/hitl" className="nav-link active">
            <span>HITL Tickets</span>
          </a>
          <a href="#" className="nav-link">
            <span>Analytics</span>
          </a>
          <a href="#" className="nav-link">
            <span>Settings</span>
          </a>
        </nav>
      </aside>
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
