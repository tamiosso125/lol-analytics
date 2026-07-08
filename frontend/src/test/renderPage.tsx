import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactElement } from "react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

/** Renderiza uma página isolada com os mesmos providers do App real
 * (QueryClient + Router). `path` é o padrão de rota (para :params via
 * useParams), `route` é a URL concreta visitada — mesma convenção do
 * App.tsx. Sem retry (erro de query falha rápido, não trava o teste). */
export function renderPage(ui: ReactElement, { path = "/", route = "/" } = {}) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>
        <Routes>
          <Route path={path} element={ui} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}
