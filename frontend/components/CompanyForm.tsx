"use client";

import { Search, Play, Square, Wand2 } from "lucide-react";
import type { ICP } from "@/lib/types";
import { Button } from "@/components/ui/button";

const DEMO_COMPANIES = ["Acme Corp", "Globex Industries"];

const DEMO_ICP: ICP = {
  target_industries: ["B2B SaaS", "Logistics tech"],
  company_sizes: ["51-200", "201-500"],
  regions: ["USA", "EU"],
  buying_signals: ["Recently raised funding", "Hiring RevOps / Sales roles"],
  value_proposition:
    "We give B2B sales teams an AI agent that researches accounts and drafts personalized outreach, saving reps ~10 hours a week.",
  sender_name: "Sam Seller",
  sender_company: "LeadBot",
  sender_role: "Founder",
};

interface Props {
  companyName: string;
  setCompanyName: (v: string) => void;
  icp: ICP;
  setIcp: (icp: ICP) => void;
  running: boolean;
  onSubmit: () => void;
  onCancel: () => void;
}

export function CompanyForm({
  companyName,
  setCompanyName,
  icp,
  setIcp,
  running,
  onSubmit,
  onCancel,
}: Props) {
  const canRun = companyName.trim().length > 0 && !running;

  function update<K extends keyof ICP>(key: K, value: ICP[K]) {
    setIcp({ ...icp, [key]: value });
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (canRun) onSubmit();
      }}
      className="rounded-2xl border border-border bg-surface p-5"
    >
      {/* Target company */}
      <label className="label-mono mb-2 block">Target company</label>
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search
            size={16}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-faint"
          />
          <input
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="e.g. Acme Corp"
            className="h-11 w-full rounded-xl border border-border bg-elevated pl-9 pr-3 text-sm text-foreground outline-none focus:border-accent/50"
          />
        </div>
        {running ? (
          <Button type="button" variant="soft" size="lg" className="press" onClick={onCancel}>
            <Square size={15} /> Stop
          </Button>
        ) : (
          <Button type="submit" variant="primary" size="lg" className="press" disabled={!canRun}>
            <Play size={15} /> Run agents
          </Button>
        )}
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-1.5">
        <span className="label-mono">Try</span>
        {DEMO_COMPANIES.map((c) => (
          <button
            key={c}
            type="button"
            onClick={() => setCompanyName(c)}
            className="press rounded-lg border border-border bg-elevated px-2.5 py-1 text-xs text-muted hover:text-foreground"
          >
            {c}
          </button>
        ))}
      </div>

      {/* Client criteria (ICP) */}
      <div className="mt-6 flex items-center justify-between">
        <label className="label-mono">Client criteria · ICP</label>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="press"
          onClick={() => setIcp(DEMO_ICP)}
        >
          <Wand2 size={13} /> Fill demo
        </Button>
      </div>

      <div className="mt-3 grid gap-3 sm:grid-cols-3">
        <TextField label="Your name" value={icp.sender_name} onChange={(v) => update("sender_name", v)} />
        <TextField label="Your company" value={icp.sender_company} onChange={(v) => update("sender_company", v)} />
        <TextField label="Your role" value={icp.sender_role} onChange={(v) => update("sender_role", v)} />
      </div>

      <div className="mt-3">
        <FieldLabel>Value proposition</FieldLabel>
        <textarea
          value={icp.value_proposition}
          onChange={(e) => update("value_proposition", e.target.value)}
          rows={2}
          placeholder="What you offer, in one or two sentences"
          className="w-full resize-y rounded-xl border border-border bg-elevated px-3 py-2 text-sm text-foreground outline-none focus:border-accent/50"
        />
      </div>

      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <ListField
          label="Target industries"
          values={icp.target_industries}
          onChange={(v) => update("target_industries", v)}
        />
        <ListField label="Company sizes" values={icp.company_sizes} onChange={(v) => update("company_sizes", v)} />
        <ListField label="Regions" values={icp.regions} onChange={(v) => update("regions", v)} />
        <ListField label="Buying signals" values={icp.buying_signals} onChange={(v) => update("buying_signals", v)} />
      </div>
    </form>
  );
}

function FieldLabel({ children }: { children: React.ReactNode }) {
  return <label className="label-mono mb-1 block">{children}</label>;
}

function TextField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <FieldLabel>{label}</FieldLabel>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="h-9 w-full rounded-lg border border-border bg-elevated px-2.5 text-sm text-foreground outline-none focus:border-accent/50"
      />
    </div>
  );
}

/** Comma-separated list editor — simple and predictable for a portfolio demo. */
function ListField({
  label,
  values,
  onChange,
}: {
  label: string;
  values: string[];
  onChange: (v: string[]) => void;
}) {
  return (
    <div>
      <FieldLabel>{label}</FieldLabel>
      <input
        value={values.join(", ")}
        onChange={(e) =>
          onChange(
            e.target.value
              .split(",")
              .map((s) => s.trim())
              .filter(Boolean),
          )
        }
        placeholder="comma, separated"
        className="h-9 w-full rounded-lg border border-border bg-elevated px-2.5 text-sm text-foreground outline-none focus:border-accent/50"
      />
    </div>
  );
}
