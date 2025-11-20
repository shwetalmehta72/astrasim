# AstraSim Frontend

Next.js App Router interface for AstraSim’s scenario builder, analytics dashboards, and AI explainers.

## Requirements

- Node.js 20+
- npm, pnpm, or yarn (examples use npm)

## Setup

```powershell
cd frontend
npm install
```

## Development

```powershell
npm run dev
```

Visit <http://localhost:3000> to view the shell UI.

## Linting & Formatting

```powershell
npm run lint
npm run format
```

Global tooling shortcuts:

```bash
./scripts/lint.sh   # Runs backend Ruff + frontend ESLint/Prettier
./scripts/check.sh  # Lint + mypy + tsc + pytest
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Global layout shell (Navbar, Sidebar, footer)
│   ├── page.tsx            # Landing hero
│   ├── screener/           # S&P 100 screener route
│   ├── scenario-builder/   # Scenario Builder workspace
│   ├── simulation/         # Monte Carlo dashboard
│   └── stock/[symbol]/     # Dynamic stock overview
├── components/             # Shared UI primitives (Navbar, Card, etc.)
└── app/globals.css         # Tailwind + design tokens
```

Add new pages under `app/<route>/page.tsx`. For nested contexts (e.g., `/stock/[symbol]`), create directories with dynamic `[param]` folders.

## Shared Components

- `Navbar` — top navigation with key routes.
- `Sidebar` — dashboard placeholder for Scenario Builder + Simulation.
- `Container` — max-width wrapper for content.
- `Card` — reusable surface for panels.
- `PageHeader` — consistent title + description block.

Future modules (Scenario Builder widgets, Simulation charts) should live beside these components or inside feature folders under `components/`.

## Design System

- Tailwind tokens defined in `tailwind.config.js` (brand colors, radii, fonts).
- Global typography + utility helpers live in `app/globals.css`.
- Favor composable Tailwind classes; if repeated patterns emerge, elevate them into components.

## Upcoming Work

- Dark/light mode toggle (T-1017).
- Skeleton loaders + shimmer placeholders (T-1018).
- Shared chart container wrappers (T-1019).
- Scenario Builder controls (P1-SP09) and Simulation dashboards (P1-SP09/10).

Track these items in `docs/meta/TASK_BACKLOG.md` and reference this README for structure guidance.

## Deployment

Use `npm run build` to produce the production bundle; Docker/devcontainer workflows are defined under `infra/`.

