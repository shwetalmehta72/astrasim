type PageHeaderProps = {
  title: string;
  description?: string;
  eyebrow?: string;
};

export default function PageHeader({ title, description, eyebrow }: PageHeaderProps) {
  return (
    <div className="space-y-2 border-b border-slate-800 pb-6">
      {eyebrow && <p className="text-xs uppercase tracking-[0.4em] text-teal-300">{eyebrow}</p>}
      <h1 className="text-4xl font-semibold text-white">{title}</h1>
      {description && <p className="max-w-3xl text-base text-slate-400">{description}</p>}
    </div>
  );
}

