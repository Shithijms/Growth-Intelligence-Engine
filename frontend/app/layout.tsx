import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DataVex Growth Intelligence Engine",
  description: "Keyword-driven growth content pipeline",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-[var(--bg)] text-[var(--text)]">
        {children}
      </body>
    </html>
  );
}
