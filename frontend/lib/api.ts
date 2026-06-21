import type { ICP, StageEvent } from "./types";

/**
 * POST to the SSE proxy and invoke `onEvent` for each streamed stage event.
 * Uses fetch streaming (not EventSource, which is GET-only) so we can send the
 * company name + ICP in the request body.
 */
export async function streamResearch(
  companyName: string,
  icp: ICP,
  onEvent: (ev: StageEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch("/api/research", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ company_name: companyName, icp }),
    signal,
  });

  if (!res.ok || !res.body) {
    throw new Error(`Research request failed (${res.status})`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE frames are separated by a blank line.
    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";

    for (const frame of frames) {
      const dataLines = frame
        .split("\n")
        .filter((l) => l.startsWith("data:"))
        .map((l) => l.slice(5).trim());
      const payload = dataLines.join("");
      if (!payload || payload === "{}") continue;
      try {
        const ev = JSON.parse(payload) as StageEvent;
        if (ev.stage) onEvent(ev);
      } catch {
        // ignore keep-alive / non-JSON frames
      }
    }
  }
}
