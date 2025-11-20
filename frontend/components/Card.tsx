import { ReactNode } from "react";

type CardProps = {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  footer?: ReactNode;
};

export default function Card({ title, subtitle, children, footer }: CardProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-950/60 shadow-xl shadow-black/40">
      {(title || subtitle) && (
        <header className="border-b border-slate-800 px-6 py-4">
          {title && <h3 className="text-lg font-semibold text-white">{title}</h3>}
          {subtitle && <p className="text-sm text-slate-400">{subtitle}</p>}
        </header>
      )}
      <div className="px-6 py-5 text-slate-200">{children}</div>
      {footer && <footer className="border-t border-slate-800 px-6 py-4 text-sm text-slate-400">{footer}</footer>}
    </section>
  );
}

