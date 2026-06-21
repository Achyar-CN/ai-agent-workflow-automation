import { config } from "@/lib/config";

// Stream from the same origin so the browser never talks to the backend
// directly (no CORS, one URL to deploy behind).
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const body = await req.text();

  let upstream: Response;
  try {
    upstream = await fetch(`${config.backendUrl}/research`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    });
  } catch {
    return Response.json(
      { error: `Cannot reach the agent backend at ${config.backendUrl}. Is it running?` },
      { status: 502 },
    );
  }

  if (!upstream.ok || !upstream.body) {
    return Response.json({ error: `Backend error ${upstream.status}` }, { status: 502 });
  }

  return new Response(upstream.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
