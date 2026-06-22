import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import AppShell from "@/components/layout/app-shell";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "OmniFlow AI — Multi-Agent Supply Chain Intelligence",
  description:
    "AI-powered multi-agent system for retail inventory optimization. Digital Twin technology for demand forecasting, disruption detection, and autonomous supply chain management.",
  keywords: "AI, supply chain, inventory optimization, multi-agent, digital twin, demand forecasting",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased`}>
        {/* Background orbs for ambient effect */}
        <div className="bg-orb bg-orb-blue" />
        <div className="bg-orb bg-orb-violet" />
        <div className="bg-orb bg-orb-emerald" />

        {/* App Layout wrapped in Client Shell */}
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
