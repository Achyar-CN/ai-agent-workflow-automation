"use client";

import { Check, Loader2, Minus, Search, Users, Target, Mail, X } from "lucide-react";
import { STAGES, type Stage, type StageStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

export type StageState = StageStatus | "pending";

const ICONS: Record<Stage, typeof Search> = {
  research: Search,
  enrich: Users,
  qualify: Target,
  draft: Mail,
};

export function PipelineProgress({ states }: { states: Record<Stage, StageState> }) {
  return (
    <ol className="flex flex-col gap-1.5" aria-label="Pipeline progress">
      {STAGES.map((stage, i) => {
        const state = states[stage.id];
        const StageIcon = ICONS[stage.id];
        return (
          <li
            key={stage.id}
            className={cn(
              "flex items-center gap-3.5 rounded-2xl border px-3.5 py-3 transition-colors duration-300",
              state === "start" && "border-accent/40 bg-accent-soft/20 glow-accent",
              state === "done" && "border-border bg-surface",
              state === "skipped" && "border-border bg-surface/60 opacity-70",
              state === "error" && "border-destructive/50 bg-destructive/5",
              state === "pending" && "border-border/60 bg-surface/40",
            )}
          >
            <StatusDot state={state} />
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <StageIcon
                  size={14}
                  className={cn(
                    state === "start" ? "text-accent" : "text-faint",
                    state === "done" && "text-foreground",
                  )}
                />
                <span
                  className={cn(
                    "text-sm font-medium",
                    state === "pending" ? "text-faint" : "text-foreground",
                  )}
                >
                  {stage.label}
                </span>
                <span className="label-mono ml-auto">
                  {state === "pending" ? "queued" : state === "start" ? "running" : state}
                </span>
              </div>
              <p className="mt-0.5 truncate text-xs text-muted">{stage.hint}</p>
            </div>
            <span className="label-mono w-4 shrink-0 text-right tabular-nums">{i + 1}</span>
          </li>
        );
      })}
    </ol>
  );
}

function StatusDot({ state }: { state: StageState }) {
  const base = "grid h-7 w-7 shrink-0 place-items-center rounded-full border";
  if (state === "start")
    return (
      <span className={cn(base, "border-accent/50 bg-accent/10 text-accent pulse-ring")}>
        <Loader2 size={14} className="animate-spin-slow" />
      </span>
    );
  if (state === "done")
    return (
      <span className={cn(base, "border-positive/50 bg-positive/10 text-positive")}>
        <Check size={14} />
      </span>
    );
  if (state === "skipped")
    return (
      <span className={cn(base, "border-border bg-elevated text-faint")}>
        <Minus size={14} />
      </span>
    );
  if (state === "error")
    return (
      <span className={cn(base, "border-destructive/50 bg-destructive/10 text-destructive")}>
        <X size={14} />
      </span>
    );
  return <span className={cn(base, "border-border bg-elevated text-faint")} />;
}
