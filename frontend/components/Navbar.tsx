import Link from "next/link";

const navLinks = [
  { href: "/screener", label: "Screener" },
  { href: "/scenario-builder", label: "Scenario Builder" },
  { href: "/simulation", label: "Simulation" },
];

export default function Navbar() {
  return (
    <header className="border-b border-slate-800 bg-slate-950/70 backdrop-blur supports-[backdrop-filter]:bg-slate-950/60">
      <nav className="mx-auto flex max-w-6xl items-center justify-between gap-6 px-6 py-4">
        <Link href="/" className="font-semibold uppercase tracking-[0.4em] text-teal-300">
          AstraSim
        </Link>
        <div className="flex items-center gap-6 text-sm text-slate-300">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="transition hover:text-white"
            >
              {link.label}
            </Link>
          ))}
          <Link
            href="/stock/AAPL"
            className="rounded-full border border-teal-400 px-4 py-1 text-xs uppercase tracking-wide text-teal-200 transition hover:bg-teal-400/10"
          >
            Stock View
          </Link>
        </div>
      </nav>
    </header>
  );
}

