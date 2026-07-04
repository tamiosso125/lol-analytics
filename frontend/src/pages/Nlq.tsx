import { useMutation } from "@tanstack/react-query";
import { Info, Send } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button, Card, CardContent, ErrorNote, Input, PageHeader, Skeleton } from "@/components/ui";
import { formatCell, humanizeColumn, isAdvisory, isEmptyResult } from "@/lib/format";
import { cn } from "@/lib/utils";
import { api, ApiError, type AskResult, type HistoryTurn } from "@/lib/api";

type Turn =
  | { type: "success"; question: string; result: AskResult }
  | {
      type: "error";
      question: string;
      message: string;
      kind: ApiError["kind"];
      sql?: string;
      cause?: string;
    };

interface Thread {
  id: number;
  turns: Turn[];
}

function turnFromError(question: string, error: ApiError): Turn {
  return {
    type: "error",
    question,
    message: error.message,
    kind: error.kind,
    sql: error.sql,
    cause: error.cause,
  };
}

function EmptyResultNote() {
  return (
    <div className="rounded-lg border border-border bg-foreground/5 px-4 py-3 text-sm text-secondary-ink">
      Nenhum resultado encontrado para esses critérios.
    </div>
  );
}

function AdvisoryNote({ result }: { result: AskResult }) {
  return (
    <div className="flex items-start gap-2.5 rounded-lg border border-border bg-foreground/5 px-4 py-3 text-sm">
      <Info size={16} className="mt-0.5 shrink-0 text-muted-ink" />
      <p className="text-secondary-ink">{String(result.rows[0]?.[0] ?? "")}</p>
    </div>
  );
}

function ResultTable({ result }: { result: AskResult }) {
  if (isEmptyResult(result)) return <EmptyResultNote />;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-secondary-ink">
            {result.columns.map((c) => (
              <th key={c} className="px-3 py-2 font-medium">
                {humanizeColumn(c)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="tabular-nums">
          {result.rows.map((row, i) => (
            <tr key={i} className="border-b border-border/50 last:border-0">
              {row.map((cell, j) => (
                <td key={j} className="px-3 py-1.5">
                  {formatCell(cell, result.columns[j])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ViewToggle({
  view,
  onChange,
}: {
  view: "sql" | "explicacao";
  onChange: (v: "sql" | "explicacao") => void;
}) {
  const tabs = [
    { key: "sql", label: "SQL" },
    { key: "explicacao", label: "Explicação" },
  ] as const;
  return (
    <div className="inline-flex rounded-lg border border-border p-0.5 text-xs">
      {tabs.map((t) => (
        <button
          key={t.key}
          onClick={() => onChange(t.key)}
          className={cn(
            "rounded-md px-2.5 py-1 font-medium transition-colors",
            view === t.key
              ? "bg-accent/10 text-accent"
              : "text-muted-ink hover:text-foreground",
          )}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}

function SuccessTurn({ question, result }: { question: string; result: AskResult }) {
  // padrão é a explicação (mais amigável que SQL cru) — busca já ao montar
  const [view, setView] = useState<"sql" | "explicacao">("explicacao");

  const explain = useMutation<{ explanation: string }, ApiError>({
    mutationFn: () => api.explain(question, result),
  });

  const showExplanation = () => {
    setView("explicacao");
    if (!explain.data && !explain.isPending) explain.mutate();
  };

  // o LLM sinalizou que não pode responder com o schema disponível
  // (SELECT '...' AS aviso) — mostra só o aviso, sem toggle SQL/Explicação
  const advisory = isAdvisory(result);

  useEffect(() => {
    if (!advisory) showExplanation();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (advisory) {
    return (
      <div>
        <p className="mb-2 text-sm font-medium text-foreground">{question}</p>
        <AdvisoryNote result={result} />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-4">
        <p className="text-sm font-medium text-foreground">{question}</p>
        <ViewToggle
          view={view}
          onChange={(v) => (v === "explicacao" ? showExplanation() : setView(v))}
        />
      </div>
      {view === "sql" ? (
        <pre className="overflow-x-auto rounded-lg bg-foreground/5 px-4 py-3 font-mono text-xs text-secondary-ink">
          {result.sql}
        </pre>
      ) : explain.isPending ? (
        <Skeleton className="h-16" />
      ) : explain.isError ? (
        <ErrorNote message={explain.error.message} kind={explain.error.kind} />
      ) : (
        <p className="rounded-lg bg-foreground/5 px-4 py-3 text-sm text-secondary-ink">
          {explain.data?.explanation}
        </p>
      )}
      <div className="mt-3">
        <ResultTable result={result} />
      </div>
    </div>
  );
}

/** Histórico (pergunta + SQL) dos turnos bem-sucedidos de uma thread —
 * dá contexto ao LLM para perguntas de acompanhamento. */
function successHistory(turns: Turn[]): HistoryTurn[] {
  return turns
    .filter((t): t is Extract<Turn, { type: "success" }> => t.type === "success")
    .map((t) => ({ question: t.question, sql: t.result.sql }));
}

function ThreadCard({ thread, onAppend }: { thread: Thread; onAppend: (turn: Turn) => void }) {
  const [followUp, setFollowUp] = useState("");

  const askFollowUp = useMutation<AskResult, ApiError, string>({
    mutationFn: (q) => api.ask(q, successHistory(thread.turns)),
    onSuccess: (result, q) => onAppend({ type: "success", question: q, result }),
    onError: (error, q) => onAppend(turnFromError(q, error)),
  });

  const submitFollowUp = () => {
    const q = followUp.trim();
    if (q && !askFollowUp.isPending) {
      askFollowUp.mutate(q);
      setFollowUp("");
    }
  };

  return (
    <Card>
      <CardContent className="space-y-4 pt-4">
        {thread.turns.map((turn, i) => (
          <div key={i} className={i > 0 ? "border-t border-border pt-4" : undefined}>
            {turn.type === "success" ? (
              <SuccessTurn question={turn.question} result={turn.result} />
            ) : (
              <div>
                <p className="mb-2 text-sm font-medium text-foreground">{turn.question}</p>
                <ErrorNote
                  message={turn.message}
                  kind={turn.kind}
                  sql={turn.sql}
                  cause={turn.cause}
                />
              </div>
            )}
          </div>
        ))}

        <div className="flex gap-2 border-t border-border pt-3">
          <Input
            value={followUp}
            onChange={(e) => setFollowUp(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submitFollowUp()}
            placeholder="Continuar esta consulta…"
            disabled={askFollowUp.isPending}
            className="text-sm"
          />
          <Button onClick={submitFollowUp} disabled={askFollowUp.isPending || !followUp.trim()}>
            <Send size={14} />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function Nlq() {
  const [question, setQuestion] = useState("");
  const [threads, setThreads] = useState<Thread[]>([]);
  const nextId = useRef(0);

  const ask = useMutation<AskResult, ApiError, string>({
    mutationFn: (q) => api.ask(q),
    onSuccess: (result, q) =>
      setThreads((ts) => [
        { id: nextId.current++, turns: [{ type: "success", question: q, result }] },
        ...ts,
      ]),
    onError: (error, q) =>
      setThreads((ts) => [{ id: nextId.current++, turns: [turnFromError(q, error)] }, ...ts]),
  });

  const submit = () => {
    const q = question.trim();
    if (q && !ask.isPending) {
      ask.mutate(q);
      setQuestion("");
    }
  };

  const appendTurn = (id: number, turn: Turn) =>
    setThreads((ts) => ts.map((t) => (t.id === id ? { ...t, turns: [...t.turns, turn] } : t)));

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="IA generativa" title="Pergunte aos dados">
        A pergunta é convertida em SQL (somente leitura, validada) e executada no banco. Cada
        card mantém o contexto — use o campo no rodapé para continuar a mesma consulta.
      </PageHeader>

      <div className="flex gap-2">
        <Input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="Ex.: qual posição tem o maior KDA médio?"
          disabled={ask.isPending}
        />
        <Button onClick={submit} disabled={ask.isPending || !question.trim()}>
          <Send size={14} />
          {ask.isPending ? "Consultando…" : "Perguntar"}
        </Button>
      </div>

      {threads.map((thread) => (
        <ThreadCard key={thread.id} thread={thread} onAppend={(turn) => appendTurn(thread.id, turn)} />
      ))}
    </div>
  );
}
