import type { Metadata } from "next";
import "./globals.css";

import Container from "@/components/Container";
import Navbar from "@/components/Navbar";
import Sidebar from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "AstraSim",
  description: "Scenario-first Monte Carlo simulator with factor-aware events.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-50 antialiased">
        <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-950 to-slate-900">
          <Navbar />
          <div className="mx-auto flex w-full max-w-6xl gap-6 px-6 py-10">
            <Sidebar />
            <main className="flex-1 space-y-8">
              <Container>{children}</Container>
            </main>
          </div>
          <footer className="border-t border-slate-900/80 bg-slate-950/80 py-6 text-center text-xs text-slate-500">
            AstraSim · Phase 1 foundations · Scenario Builder + Simulation coming soon
          </footer>
        </div>
      </body>
    </html>
  );
}

