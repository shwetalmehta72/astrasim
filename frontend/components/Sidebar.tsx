const sections = [
  { label: "Overview", href: "#" },
  { label: "Factors", href: "#" },
  { label: "Events", href: "#" },
  { label: "Simulation", href: "#" },
  { label: "Exports", href: "#" },
];

export default function Sidebar() {
  return (
    <aside className="hidden w-64 flex-col border-r border-slate-800 bg-slate-950/60 p-4 text-sm text-slate-300 lg:flex">
      <p className="mb-4 text-xs uppercase tracking-[0.3em] text-slate-500">Workspace</p>
      <nav className="flex flex-col gap-2">
        {sections.map((section) => (
          <button
            key={section.label}
            type="button"
            className="rounded-md px-3 py-2 text-left transition hover:bg-slate-800 hover:text-white"
          >
            {section.label}
          </button>
        ))}
      </nav>
      <div className="mt-auto rounded-md border border-slate-800/80 bg-slate-900/60 p-3 text-xs text-slate-400">
        Sidebar content placeholder. Future prompts will surface scenario controls and state summaries.
      </div>
    </aside>
  );
}

