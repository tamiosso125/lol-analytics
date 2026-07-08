import { AlertTriangle } from "lucide-react";
import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

/** Error boundaries só funcionam como class component (a API do React
 * não tem equivalente em hooks) — captura exceções de render em
 * qualquer página filha e mostra um fallback em vez de tela branca. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Erro não tratado na página:", error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3 text-center">
          <AlertTriangle size={28} className="text-chart-red" />
          <p className="text-lg font-semibold text-foreground">Esta página quebrou</p>
          <p className="max-w-md text-sm text-secondary-ink">
            Um erro inesperado impediu esta página de renderizar. Tente recarregar; se
            persistir, é um bug — o detalhe técnico foi para o console do navegador.
          </p>
          <pre className="mt-1 max-w-lg overflow-x-auto rounded-md bg-foreground/5 px-3 py-2 text-left font-mono text-xs text-secondary-ink">
            {this.state.error.message}
          </pre>
          <button
            onClick={() => this.setState({ error: null })}
            className="mt-1 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:opacity-90"
          >
            Tentar de novo
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
