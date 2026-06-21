/** Centralized env-driven config (server-side).
 *  BACKEND_URL points at the FastAPI multi-agent service. */
export const config = {
  backendUrl: process.env.BACKEND_URL ?? "http://127.0.0.1:8000",
} as const;
