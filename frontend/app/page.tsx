"use client";

import { useRef, useState } from "react";
import { Bot, Sparkles, ShieldCheck, AlertTriangle } from "lucide-react";
import { streamResearch } from "@/lib/api";
import {
  EMPTY_ICP,
  type CompanyProfile,
  type EmailDraft,
  type ICP,
  type KeyPerson,
  type Qualification,
  type Stage,
} from "@/lib/types";
import { CompanyForm } from "@/components/CompanyForm";
import { PipelineProgress, type StageState } from "@/components/PipelineProgress";
import { CompanyProfileCard } from "@/components/CompanyProfileCard";
import { KeyPeopleList } from "@/components/KeyPeopleList";
import { QualificationPanel } from "@/components/QualificationPanel";
import { EmailDraftCard } from "@/components/EmailDraftCard";

const INITIAL_STAGES: Record<Stage, StageState> = {
  research: "pending",
  enrich: "pending",
  qualify: "pending",
  draft: "pending",
};

export default function Home() {
  const [companyName, setCompanyName] = useState("");
  const [icp, setIcp] = useState<ICP>(EMPTY_ICP);

  const [stages, setStages] = useState<Record<Stage, StageState>>(INITIAL_STAGES);
  const [profile, setProfile] = useState<CompanyProfile | null>(null);
  const [people, setPeople] = useState<KeyPerson[] | null>(null);
  const [qual, setQual] = useState<Qualification | null>(null);
  const [email, setEmail] = useState<EmailDraft | null>(null);

  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasRun, setHasRun] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  async function handleSubmit() {
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;

    setStages(INITIAL_STAGES);
    setProfile(null);
    setPeople(null);
    setQual(null);
    setEmail(null);
    setError(null);
    setRunning(true);
    setHasRun(true);

    try {
      await streamResearch(
        companyName.trim(),
        icp,
        (ev) => {
          setStages((prev) => ({ ...prev, [ev.stage]: ev.status }));
          if (ev.status === "error") setError(ev.message ?? "Something went wrong.");
          if (ev.status !== "done" || !ev.data) return;
          if (ev.stage === "research") setProfile(ev.data as unknown as CompanyProfile);
          else if (ev.stage === "enrich")
            setPeople((ev.data.people as KeyPerson[]) ?? []);
          else if (ev.stage === "qualify") setQual(ev.data as unknown as Qualification);
          else if (ev.stage === "draft") setEmail(ev.data as unknown as EmailDraft);
        },
        ctrl.signal,
      );
    } catch (e) {
      if (!ctrl.signal.aborted) setError(e instanceof Error ? e.message : "Request failed.");
    } finally {
      setRunning(false);
    }
  }

  function handleCancel() {
    abortRef.current?.abort();
    setRunning(false);
  }

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:py-12">
      <header className="mb-8 flex items-start gap-3.5">
        <span className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl border border-accent/30 bg-accent-soft/20 text-accent glow-accent">
          <Bot size={20} />
        </span>
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            AI Sales Lead Researcher
          </h1>
          <p className="mt-1 max-w-xl text-sm text-muted">
            A four-agent pipeline researches a company, finds key people, scores fit against your
            ICP, and drafts a personalized cold email — live.
          </p>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,440px)_1fr]">
        {/* Control column */}
        <div className="flex flex-col gap-5 lg:sticky lg:top-8 lg:self-start">
          <CompanyForm
            companyName={companyName}
            setCompanyName={setCompanyName}
            icp={icp}
            setIcp={setIcp}
            running={running}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
          />
          {hasRun && <PipelineProgress states={stages} />}
        </div>

        {/* Results column */}
        <div className="flex flex-col gap-5">
          {error && (
            <div className="flex items-start gap-2.5 rounded-2xl border border-destructive/40 bg-destructive/5 px-4 py-3 text-sm text-foreground">
              <AlertTriangle size={16} className="mt-0.5 shrink-0 text-destructive" />
              <span>{error}</span>
            </div>
          )}

          {!hasRun && <EmptyState />}

          {profile && <CompanyProfileCard profile={profile} />}
          {people && <KeyPeopleList people={people} />}
          {qual && <QualificationPanel qual={qual} />}
          {email && <EmailDraftCard draft={email} />}

          {qual?.verdict === "NO_GO" && stages.draft === "skipped" && (
            <p className="rounded-2xl border border-border bg-surface/60 px-4 py-3 text-sm text-muted">
              Lead scored below your fit threshold — the agent skipped drafting an email. This is the
              pipeline making a real qualification decision, not a failure.
            </p>
          )}
        </div>
      </div>
    </main>
  );
}

function EmptyState() {
  const steps = [
    "Research the company from public web sources",
    "Extract key decision-makers (public data only — no LinkedIn scraping)",
    "Score fit against your Ideal Customer Profile",
    "Draft a personalized cold email for qualified leads",
  ];
  return (
    <div className="rounded-2xl border border-dashed border-border bg-surface/40 p-8">
      <span className="grid h-10 w-10 place-items-center rounded-xl border border-border bg-elevated text-accent">
        <Sparkles size={18} />
      </span>
      <h2 className="mt-4 text-base font-semibold text-foreground">Enter a company to begin</h2>
      <p className="mt-1 text-sm text-muted">The agents will work through four stages:</p>
      <ol className="mt-4 flex flex-col gap-2.5">
        {steps.map((s, i) => (
          <li key={s} className="flex items-start gap-3 text-sm text-muted">
            <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full border border-border bg-elevated font-mono text-xs text-faint">
              {i + 1}
            </span>
            {s}
          </li>
        ))}
      </ol>
      <p className="mt-5 flex items-center gap-2 border-t border-border pt-4 text-xs text-faint">
        <ShieldCheck size={13} />
        Uses only public data + a curated demo set. No LinkedIn scraping.
      </p>
    </div>
  );
}
