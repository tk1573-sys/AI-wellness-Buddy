import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "react-hot-toast";

export const metadata: Metadata = {
  title: "AI Wellness Buddy",
  description: "Your empathetic AI companion for emotional wellbeing",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="font-sans bg-gray-950 text-gray-100 antialiased">
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: "rgba(17,24,39,0.95)",
              color: "#f3f4f6",
              border: "1px solid rgba(255,255,255,0.12)",
              backdropFilter: "blur(12px)",
            },
          }}
        />
      </body>
    </html>
  );
}
