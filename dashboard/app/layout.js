import "./globals.css";

export const metadata = {
  title: "Hotel AI",
  description: "AI-powered Hotel Booking",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
