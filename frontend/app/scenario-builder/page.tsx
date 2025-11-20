import type { Metadata } from "next";

import Card from "@/components/Card";
import PageHeader from "@/components/PageHeader";

export const metadata: Metadata = {
  title: "AstraSim — Scenario Builder",
};

export default function ScenarioBuilderPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Scenarios"
        title="Scenario Builder"
        description="Configure macro, AI, earnings, and execution viewpoints. Sliders, T-shirt sizing, and guardrails will arrive in Phase 1 Sub-Phase 9."
      />
      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Viewpoint Controls" subtitle="Sliders + T-shirt sizing">
          <p className="text-sm text-slate-300">
            Controls for Macro Risk, AI Trend, Earnings Risk, and Execution Quality will mount here.
            Today&apos;s stub demonstrates the component shell.
          </p>
        </Card>
        <Card title="Event Stack" subtitle="Factor-driven events">
          <p className="text-sm text-slate-300">
            Event templates tied to factor states will show up here with probability and impact guardrails.
          </p>
        </Card>
      </div>
    </div>
  );
}

