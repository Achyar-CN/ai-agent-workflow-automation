"use client";

import { Users, ExternalLink, Mail } from "lucide-react";
import type { KeyPerson } from "@/lib/types";

function initials(name: string): string {
  return name
    .split(/\s+/)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? "")
    .join("");
}

export function KeyPeopleList({ people }: { people: KeyPerson[] }) {
  return (
    <section className="animate-fade-up rounded-2xl border border-border bg-surface p-5">
      <header className="mb-4 flex items-center gap-2">
        <Users size={15} className="text-accent" />
        <h2 className="text-sm font-semibold text-foreground">Key people</h2>
        <span className="label-mono ml-auto">{people.length} found</span>
      </header>

      {people.length === 0 ? (
        <p className="text-sm text-muted">
          No public decision-makers found. Try a company with a public team or leadership page.
        </p>
      ) : (
        <ul className="flex flex-col divide-y divide-border">
          {people.map((p) => (
            <li key={`${p.name}-${p.title}`} className="flex items-start gap-3 py-3 first:pt-0 last:pb-0">
              <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full border border-border bg-elevated text-xs font-semibold text-accent">
                {initials(p.name) || "?"}
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-foreground">{p.name}</span>
                  {p.title && <span className="text-sm text-muted">· {p.title}</span>}
                </div>
                {p.relevance && <p className="mt-0.5 text-xs text-muted">{p.relevance}</p>}
                <div className="mt-1.5 flex flex-wrap items-center gap-3">
                  {p.email_guess && (
                    <span className="inline-flex items-center gap-1 text-xs text-faint">
                      <Mail size={11} />
                      {p.email_guess}
                    </span>
                  )}
                  {p.source_url && (
                    <a
                      href={p.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-faint hover:text-accent hover:underline"
                    >
                      <ExternalLink size={11} />
                      source
                    </a>
                  )}
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
