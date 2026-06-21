"use client";

import { Target, Check, AlertCircle } from "lucide-react";
import type { Qualification } from "@/lib/types";
import { cn } from "@/lib/utils";

export function QualificationPanel({ qual }: { qual: Qualification }) {
  const go = qual.verdict === "GO";

  return (
    <section className="animate-fade-up rounded-2xl border border-border bg-surface p-5">
      <header className="mb-4 flex items-center gap-2">
        <Target size={15} className="text-accent" />
        <h2 className="text-sm font-semibold text-foreground">Qualification</h2>
        <span
          className={cn(
            "ml-auto rounded-full px-2.5 py-1 text-xs font-semibold",
            go
              ? "bg-positive/15 text-positive"
              : "bg-destructive/15 text-destructive",
          )}
        >
          {go ? "GO" : "NO-GO"}
        </span>
      </header>

      <div className="flex items-end justify-between gap-4">
        <span className="text-sm text-muted">Fit score</span>
        <span className="font-mono text-2xl font-semibold tabular-nums text-foreground">
          {qual.fit_score}
          <span className="text-sm text-faint">/100</span>
        </span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-elevated">
        <div
          className={cn("h-full rounded-full transition-all duration-700", go ? "bg-positive" : "bg-destructive")}
          style={{ width: `${qual.fit_score}%` }}
        />
      </div>

      {qual.reasoning && (
        <p className="mt-4 text-sm leading-relaxed text-muted">{qual.reasoning}</p>
      )}

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        {qual.matched_criteria.length > 0 && (
          <div>
            <p className="label-mono mb-2">Matched</p>
            <ul className="space-y-1.5">
              {qual.matched_criteria.map((c) => (
                <li key={c} className="flex gap-2 text-sm text-muted">
                  <Check size={14} className="mt-0.5 shrink-0 text-positive" />
                  {c}
                </li>
              ))}
            </ul>
          </div>
        )}
        {qual.gaps.length > 0 && (
          <div>
            <p className="label-mono mb-2">Gaps</p>
            <ul className="space-y-1.5">
              {qual.gaps.map((g) => (
                <li key={g} className="flex gap-2 text-sm text-muted">
                  <AlertCircle size={14} className="mt-0.5 shrink-0 text-faint" />
                  {g}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}
