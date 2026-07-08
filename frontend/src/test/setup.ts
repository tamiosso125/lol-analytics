import "@testing-library/jest-dom/vitest";

// jsdom não implementa ResizeObserver — o Recharts (ResponsiveContainer)
// usa isso internamente em todo gráfico; sem o stub, qualquer página com
// gráfico lança "ResizeObserver is not defined" no render.
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver = ResizeObserverStub;
