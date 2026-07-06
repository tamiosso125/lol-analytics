/** Primitivas de UI no estilo shadcn/ui (mínimas, sem dependência do CLI). */
import { cn } from "@/lib/utils";
import { AlertTriangle, Info, WifiOff } from "lucide-react";
import type { ComponentProps, ReactNode } from "react";

/** Cabeçalho hextech padrão das páginas: rótulo dourado + título serifado
 * + linha de brilho — a mesma identidade visual do herói da Home. */
export function PageHeader({
  eyebrow,
  title,
  children,
}: {
  eyebrow: string;
  title: string;
  children?: ReactNode;
}) {
  return (
    <div>
      <p className="hextech-title text-[11px] font-medium text-gold">{eyebrow}</p>
      <h1 className="hextech-title mt-1 text-2xl font-semibold text-gold-bright">{title}</h1>
      <div className="mt-2 h-px max-w-3xl bg-linear-to-r from-gold/50 via-gold/20 to-transparent" />
      {children && (
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-secondary-ink">{children}</p>
      )}
    </div>
  );
}

export function Card({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      className={cn("rounded-xl border border-border bg-card shadow-sm", className)}
      {...props}
    />
  );
}

export function CardHeader({ className, ...props }: ComponentProps<"div">) {
  return <div className={cn("px-5 pt-4 pb-2", className)} {...props} />;
}

export function CardTitle({ className, ...props }: ComponentProps<"h3">) {
  return (
    <h3
      className={cn("text-sm font-medium text-secondary-ink tracking-tight", className)}
      {...props}
    />
  );
}

export function CardContent({ className, ...props }: ComponentProps<"div">) {
  return <div className={cn("px-5 pb-4", className)} {...props} />;
}

export function Button({ className, ...props }: ComponentProps<"button">) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg bg-accent px-4 py-2",
        "text-sm font-medium text-white transition-opacity hover:opacity-90",
        "disabled:pointer-events-none disabled:opacity-50",
        className,
      )}
      {...props}
    />
  );
}

export function Input({ className, ...props }: ComponentProps<"input">) {
  return (
    <input
      className={cn(
        "w-full rounded-lg border border-border bg-card px-3 py-2 text-sm",
        "placeholder:text-muted-ink focus:outline-none focus:ring-2 focus:ring-accent/40",
        className,
      )}
      {...props}
    />
  );
}

export function Skeleton({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      className={cn("animate-pulse rounded-lg bg-foreground/10", className)}
      {...props}
    />
  );
}

const ERROR_KIND = {
  validation: {
    icon: Info,
    title: "Não foi possível responder",
    className: "border-border bg-foreground/5 text-secondary-ink",
  },
  network: {
    icon: WifiOff,
    title: "Falha de conexão com a API",
    className: "border-chart-red/40 bg-chart-red/10",
  },
  server: {
    icon: AlertTriangle,
    title: "Erro no servidor",
    className: "border-chart-red/40 bg-chart-red/10",
  },
} as const;

/** Cabeçalho de seção dentro de uma página (menor que PageHeader) —
 * eyebrow dourado + título, com descrição opcional. */
export function SectionTitle({
  eyebrow,
  title,
  desc,
}: {
  eyebrow: string;
  title: string;
  desc?: string;
}) {
  return (
    <div className="pt-2">
      <p className="hextech-title text-[11px] font-medium text-gold">{eyebrow}</p>
      <h2 className="mt-0.5 text-lg font-semibold tracking-tight">{title}</h2>
      {desc && <p className="mt-0.5 text-sm text-secondary-ink">{desc}</p>}
    </div>
  );
}

/** Frase de conclusão sob um gráfico/tabela — mesmo padrão em todas as
 * páginas de stats (Dashboard, Competitivo). */
export function Takeaway({ children }: { children: ReactNode }) {
  return (
    <p className="mt-2 border-t border-border pt-2 text-xs leading-relaxed text-secondary-ink">
      <span className="font-medium text-gold">Leitura: </span>
      {children}
    </p>
  );
}

/** Cartão de KPI/estatística: rótulo + número grande + dica opcional.
 * `size="sm"` é a variante compacta (borda simples, sem Card/CardHeader)
 * usada em grades densas de várias métricas lado a lado. */
export function StatCard({
  label,
  value,
  hint,
  size = "lg",
}: {
  label: string;
  value: string | number;
  hint?: string;
  size?: "sm" | "lg";
}) {
  if (size === "sm") {
    return (
      <div className="rounded-lg border border-border bg-card px-4 py-3">
        <p className="text-xs text-muted-ink">{label}</p>
        <p className="mt-0.5 text-xl font-semibold tabular-nums tracking-tight">{value}</p>
        {hint && <p className="mt-0.5 text-xs text-muted-ink">{hint}</p>}
      </div>
    );
  }
  return (
    <Card>
      <CardHeader>
        <CardTitle>{label}</CardTitle>
      </CardHeader>
      <CardContent>
        <span className="text-3xl font-semibold tabular-nums tracking-tight">{value}</span>
        {hint && <p className="mt-1 text-xs text-muted-ink">{hint}</p>}
      </CardContent>
    </Card>
  );
}

export function ErrorNote({
  message,
  kind = "server",
  sql,
  cause,
}: {
  message: string;
  kind?: keyof typeof ERROR_KIND;
  /** SQL gerada e erro real do banco — diagnóstico técnico opcional,
   * mostrado para dar pra debugar em vez de só "tente reformular". */
  sql?: string;
  cause?: string;
}) {
  const { icon: Icon, title, className } = ERROR_KIND[kind];
  return (
    <div className={cn("flex items-start gap-2.5 rounded-lg border px-4 py-3 text-sm", className)}>
      <Icon size={16} className="mt-0.5 shrink-0" />
      <div className="min-w-0 flex-1">
        <p className="font-medium text-foreground">{title}</p>
        <p className="mt-0.5 text-secondary-ink">{message}</p>
        {(sql || cause) && (
          <div className="mt-2 space-y-1.5">
            {sql && (
              <pre className="overflow-x-auto rounded-md bg-foreground/5 px-3 py-2 font-mono text-xs text-secondary-ink">
                {sql}
              </pre>
            )}
            {cause && (
              <p className="font-mono text-xs text-secondary-ink">
                <span className="text-muted-ink">Erro do banco: </span>
                {cause}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
