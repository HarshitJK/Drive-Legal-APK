// Typed API client for DriveLegal backend
// All calls go through Vite proxy → http://localhost:8000

export interface ChatRequest {
  message: string;
  session_id: string;
  language?: string;
  state?: string;
  city?: string;
}

export interface ChatResponse {
  reply: string;
  language: string;
  parivahan_link?: string | null;
  session_id: string;
}

export interface CalculatorRequest {
  violation: string;
  vehicle_type: string;
  state: string;
  offense_count: string;
  session_id?: string;
}

export interface CalculatorResponse {
  violation: string;
  section: string;
  vehicle_type: string;
  state: string;
  offense: string;
  fine_min: number;
  fine_max: number;
  fine_display: string;
  state_note?: string | null;
  parivahan_link: string;
}

export interface LocationRequest {
  session_id: string;
  text?: string;
  latitude?: number;
  longitude?: number;
}

export interface LocationResponse {
  state: string;
  city: string;
  country: string;
}

// In development, Vite proxies /api → localhost:8000
// In production (Capacitor mobile), we must use the real backend URL
const PROD_API_URL = import.meta.env.VITE_API_URL ?? "http://10.0.2.2:8000";
const BASE_URL = import.meta.env.DEV ? "/api" : PROD_API_URL;

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? `HTTP ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export const api = {
  sendChat: (body: ChatRequest): Promise<ChatResponse> =>
    request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  calculateFine: (body: CalculatorRequest): Promise<CalculatorResponse> =>
    request<CalculatorResponse>("/calculator", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  setLocation: (body: LocationRequest): Promise<LocationResponse> =>
    request<LocationResponse>("/location", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  setLanguage: (session_id: string, language: string) =>
    request("/language", {
      method: "POST",
      body: JSON.stringify({ session_id, language }),
    }),

  health: () => request("/health"),
};

// ── Session ID ────────────────────────────────────────────────────────────────
const SESSION_KEY = "drivelegal_session_id";

export function getOrCreateSessionId(): string {
  const existing = localStorage.getItem(SESSION_KEY);
  if (existing) return existing;
  const id = crypto.randomUUID();
  localStorage.setItem(SESSION_KEY, id);
  return id;
}
