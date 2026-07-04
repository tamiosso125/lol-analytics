import { BarChart3, Gamepad2, Home, MessageSquareText, Moon, ScanEye, Sun, Swords, Target, Trophy, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { cn } from "@/lib/utils";

const NAV = [
  { to: "/", label: "Início", icon: Home },
  { to: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { to: "/campeoes", label: "Campeões", icon: Users },
  { to: "/partidas", label: "Partidas", icon: Swords },
  { to: "/competitivo", label: "Competitivo", icon: Trophy },
  { to: "/consulta", label: "Consulta NL", icon: MessageSquareText },
  { to: "/predicao", label: "Predição", icon: Target },
  { to: "/montar", label: "Montar partida", icon: Gamepad2 },
  { to: "/explicabilidade", label: "Explicabilidade", icon: ScanEye },
];

function ThemeToggle() {
  const [dark, setDark] = useState(() =>
    document.documentElement.classList.contains("dark"),
  );
  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);
  return (
    <button
      onClick={() => setDark(!dark)}
      aria-label={dark ? "Mudar para tema claro" : "Mudar para tema escuro"}
      className="rounded-lg border border-border p-2 text-secondary-ink hover:text-foreground"
    >
      {dark ? <Sun size={16} /> : <Moon size={16} />}
    </button>
  );
}

export function Layout() {
  return (
    <div className="flex min-h-screen">
      <aside className="flex w-56 shrink-0 flex-col border-r border-border bg-card px-3 py-5">
        <div className="mb-6 px-2">
          <span className="hextech-title text-base font-semibold text-gold-bright">
            Belles<span className="text-gold">traiko</span>
          </span>
          <p className="text-xs text-muted-ink">Plataforma de análise — TCC</p>
        </div>
        <nav className="flex flex-col gap-1">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm",
                  isActive
                    ? "bg-accent/10 font-medium text-accent"
                    : "text-secondary-ink hover:bg-foreground/5 hover:text-foreground",
                )
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto flex items-center justify-between px-2">
          <span className="text-xs text-muted-ink">Tema</span>
          <ThemeToggle />
        </div>
      </aside>
      <main className="min-w-0 flex-1 px-8 py-6">
        <Outlet />
      </main>
    </div>
  );
}
