import type { Metadata } from "next";

import Card from "@/components/Card";
import PageHeader from "@/components/PageHeader";

export const metadata: Metadata = {
  title: "AstraSim — Screener",
};

export default function ScreenerPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Phase 1"
        title="S&P 100 Screener"
        description="Surface large-cap names, volatility context, and regime callouts. This placeholder will evolve into a sortable grid with filters."
      />
      <Card title="Coming Soon" subtitle="Universe overview">
        <p className="text-slate-300">
          Screener data will appear here once ingestion pipelines are active. Expect columns for
          realized/implied volatility, YTD performance, and upcoming catalysts.
        </p>
      </Card>
    </div>
  );
}

