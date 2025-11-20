import type { Metadata } from "next";

import Card from "@/components/Card";
import PageHeader from "@/components/PageHeader";

type StockPageProps = {
  params: { symbol: string };
};

export async function generateMetadata({ params }: StockPageProps): Promise<Metadata> {
  const symbol = params.symbol?.toUpperCase() ?? "Stock";
  return {
    title: `AstraSim — ${symbol}`,
  };
}

export default function StockPage({ params }: StockPageProps) {
  const symbol = params.symbol?.toUpperCase() ?? "TICKER";

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Stock Overview"
        title={`${symbol} snapshot`}
        description="Regimes, factor states, liquidity, and AI context will live here. For now, this page ensures routing and layout work for dynamic tickers."
      />
      <div className="grid gap-6 md:grid-cols-2">
        <Card title="Regime Context">
          <p className="text-sm text-slate-300">
            Rule-based regimes and volatility callouts will render in this panel once analytics are available.
          </p>
        </Card>
        <Card title="Upcoming Catalysts">
          <p className="text-sm text-slate-300">
            Earnings, macro events, and AI signals will populate this section in future prompts.
          </p>
        </Card>
      </div>
    </div>
  );
}

