"use client";

import { Building2, MapPin, Users2, Factory, ExternalLink } from "lucide-react";
import type { CompanyProfile } from "@/lib/types";

export function CompanyProfileCard({ profile }: { profile: CompanyProfile }) {
  const meta = [
    { icon: Factory, value: profile.industry },
    { icon: Users2, value: profile.size },
    { icon: MapPin, value: profile.location },
  ].filter((m) => m.value);

  return (
    <section className="animate-fade-up rounded-2xl border border-border bg-surface p-5">
      <header className="flex items-start gap-3">
        <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl border border-border bg-elevated text-accent">
          <Building2 size={18} />
        </span>
        <div className="min-w-0">
          <h2 className="text-lg font-semibold leading-tight text-foreground">{profile.name}</h2>
          {profile.website && (
            <a
              href={profile.website}
              target="_blank"
              rel="noreferrer"
              className="mt-0.5 inline-flex items-center gap-1 text-xs text-accent hover:underline"
            >
              {profile.website.replace(/^https?:\/\//, "")}
              <ExternalLink size={11} />
            </a>
          )}
        </div>
      </header>

      {meta.length > 0 && (
        <dl className="mt-4 flex flex-wrap gap-x-5 gap-y-2">
          {meta.map(({ icon: Icon, value }) => (
            <div key={value} className="flex items-center gap-1.5 text-sm text-muted">
              <Icon size={13} className="text-faint" />
              {value}
            </div>
          ))}
        </dl>
      )}

      {profile.description && (
        <p className="mt-4 text-sm leading-relaxed text-muted">{profile.description}</p>
      )}

      {profile.products.length > 0 && (
        <div className="mt-4">
          <p className="label-mono mb-2">Products</p>
          <div className="flex flex-wrap gap-1.5">
            {profile.products.map((p) => (
              <span
                key={p}
                className="rounded-lg border border-border bg-elevated px-2.5 py-1 text-xs text-foreground"
              >
                {p}
              </span>
            ))}
          </div>
        </div>
      )}

      {profile.recent_signals.length > 0 && (
        <div className="mt-4">
          <p className="label-mono mb-2">Recent signals</p>
          <ul className="space-y-1.5">
            {profile.recent_signals.map((s) => (
              <li key={s} className="flex gap-2 text-sm text-muted">
                <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-accent" />
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {profile.sources.length > 0 && (
        <footer className="mt-4 flex flex-wrap items-center gap-2 border-t border-border pt-3">
          <span className="label-mono">Sources</span>
          {profile.sources.map((url) => (
            <a
              key={url}
              href={url}
              target="_blank"
              rel="noreferrer"
              className="max-w-[14rem] truncate text-xs text-faint hover:text-accent hover:underline"
            >
              {url.replace(/^https?:\/\//, "")}
            </a>
          ))}
        </footer>
      )}
    </section>
  );
}
