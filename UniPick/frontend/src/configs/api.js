export const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const MOCK_APIS = import.meta.env.VITE_MOCK_APIS == "true";

export const MOCK_DELAY_MS = Number(import.meta.env.VITE_MOCK_DELAY_MS ?? 300);
