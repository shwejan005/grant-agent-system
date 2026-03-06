import type { Metadata } from "next";
import { League_Spartan, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const spartan = League_Spartan({
  subsets: ["latin"],
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Grant Proposal Generator",
  description: "CrewAI multi-agent system for SERB research grant proposal generation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="antialiased">
      <body
        className={`${spartan.className} bg-background text-foreground overflow-x-hidden min-h-screen relative`}
      >
        <div className="absolute inset-0 bg-grid-pattern opacity-10 pointer-events-none -z-10" />
        {children}
      </body>
    </html>
  );
}
