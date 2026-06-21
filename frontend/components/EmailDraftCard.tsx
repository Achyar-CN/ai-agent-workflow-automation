"use client";

import { useEffect, useState } from "react";
import { Mail, Copy, Check, Sparkles } from "lucide-react";
import type { EmailDraft } from "@/lib/types";
import { Button } from "@/components/ui/button";

export function EmailDraftCard({ draft }: { draft: EmailDraft }) {
  const [subject, setSubject] = useState(draft.subject);
  const [body, setBody] = useState(draft.body);
  const [copied, setCopied] = useState(false);

  // Re-sync when a fresh draft streams in.
  useEffect(() => {
    setSubject(draft.subject);
    setBody(draft.body);
  }, [draft]);

  async function copy() {
    await navigator.clipboard.writeText(`Subject: ${subject}\n\n${body}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  }

  return (
    <section className="animate-fade-up rounded-2xl border border-accent/30 bg-surface p-5 glow-accent">
      <header className="mb-4 flex items-center gap-2">
        <Mail size={15} className="text-accent" />
        <h2 className="text-sm font-semibold text-foreground">Personalized cold email</h2>
        {draft.recipient && (
          <span className="text-xs text-muted">→ {draft.recipient}</span>
        )}
        <Button size="sm" variant="soft" className="ml-auto press" onClick={copy}>
          {copied ? <Check size={14} className="text-positive" /> : <Copy size={14} />}
          {copied ? "Copied" : "Copy"}
        </Button>
      </header>

      <label className="label-mono mb-1 block">Subject</label>
      <input
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
        className="mb-3 w-full rounded-xl border border-border bg-elevated px-3 py-2 text-sm text-foreground outline-none focus:border-accent/50"
      />

      <label className="label-mono mb-1 block">Body</label>
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        rows={9}
        className="prose-email w-full resize-y rounded-xl border border-border bg-elevated px-3 py-2.5 text-sm text-foreground outline-none focus:border-accent/50"
      />

      {draft.personalization_hooks.length > 0 && (
        <div className="mt-4">
          <p className="label-mono mb-2 flex items-center gap-1.5">
            <Sparkles size={11} className="text-accent" /> Personalization hooks
          </p>
          <div className="flex flex-wrap gap-1.5">
            {draft.personalization_hooks.map((h) => (
              <span
                key={h}
                className="rounded-lg border border-accent/25 bg-accent-soft/20 px-2.5 py-1 text-xs text-foreground"
              >
                {h}
              </span>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
