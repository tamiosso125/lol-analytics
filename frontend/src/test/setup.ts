import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

import "@testing-library/jest-dom/vitest";

// sem `globals: true` no vite.config.ts, o @testing-library/react não
// acha um `afterEach` global pra registrar limpeza automática — sem
// isso, o DOM de um teste vaza pro próximo dentro do mesmo arquivo
// (getByRole passa a achar elementos duplicados de renders antigos).
afterEach(cleanup);

// jsdom não implementa ResizeObserver — o Recharts (ResponsiveContainer)
// usa isso internamente em todo gráfico; sem o stub, qualquer página com
// gráfico lança "ResizeObserver is not defined" no render.
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver = ResizeObserverStub;
