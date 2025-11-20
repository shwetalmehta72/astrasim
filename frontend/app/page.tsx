export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-4xl flex-col justify-center gap-6 px-6">
      <span className="text-sm uppercase tracking-[0.3em] text-teal-300">
        AstraSim · Phase 1
      </span>
      <h1 className="text-4xl font-semibold leading-tight text-white">
        Scenario-first Monte Carlo simulator
      </h1>
      <p className="text-lg text-slate-300">
        Backend, data, and UI scaffolding are live. Upcoming prompts will add
        regime detection, factor modeling, and the Scenario Builder experience.
      </p>
    </main>
  );
}

