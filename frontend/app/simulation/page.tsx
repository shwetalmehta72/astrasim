import type { Metadata } from "next";

import Card from "@/components/Card";
import PageHeader from "@/components/PageHeader";

export const metadata: Metadata = {
  title: "AstraSim — Simulation Dashboard",
};

export default function SimulationPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Simulation"
        title="Monte Carlo Dashboard"
        description="Distribution charts, quantiles, tail risks, and options comparisons will render in this workspace after the MC engine lands."
      />
      <div className="grid gap-6 md:grid-cols-2">
        <Card title="Distribution Overview">
          <p className="text-sm text-slate-300">
            Histogram, KDE, and quantile tables will occupy this section. Hooking into the Monte Carlo engine is a
            later milestone.
          </p>
        </Card>
        <Card title="Scenario Comparison">
          <p className="text-sm text-slate-300">
            Users will be able to contrast base, bullish, and bearish scenarios, plus compare vs options implied moves.
          </p>
        </Card>
      </div>
    </div>
  );
}

