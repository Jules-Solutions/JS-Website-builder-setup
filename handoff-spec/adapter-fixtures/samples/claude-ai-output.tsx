/*
{
  "$schema": "spec/component-output-v1.json",
  "$version": "v1",
  "type": "component-output",
  "brief_id": "subscribe-card-2026-06-14T17-05-00Z",
  "tool_used": "claude-ai",
  "timestamp": "2026-06-14T17:09:00Z",
  "files": [
    { "path": "components/SubscribeCard.tsx", "content_below": true }
  ],
  "self_assessment": {
    "addressed_iteration_issues": true,
    "deviations_from_brief": []
  }
}
*/

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

type SubscribeCardProps = {
  heading: string
  blurb: string
  cta_text: string
  on_submit: (email: string) => Promise<void>
}

export function SubscribeCard({ heading, blurb, cta_text, on_submit }: SubscribeCardProps) {
  const [email, setEmail] = useState("")
  const [status, setStatus] = useState<"default" | "loading" | "success" | "error">("default")
  const [error, setError] = useState("")

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setStatus("loading")
    try {
      await on_submit(email)
      setStatus("success")
    } catch (err) {
      setError("That didn't work. Try again?")
      setStatus("error")
    }
  }

  return (
    <section className="rounded-xl bg-[oklch(98%_0_0)] px-4 py-8 md:px-8 dark:bg-[oklch(15%_0_0)]">
      <h2 className="font-serif text-3xl font-semibold text-[oklch(15%_0_0)] dark:text-[oklch(98%_0_0)]">
        {heading}
      </h2>
      <p className="mt-2 font-sans text-lg text-[oklch(15%_0_0)]/80">{blurb}</p>

      {status === "success" ? (
        <p className="mt-6 font-sans text-[oklch(70%_0.15_145)]" role="status">
          You're in. Check your inbox.
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-3 md:flex-row">
          <Input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            aria-label="Email address"
            disabled={status === "loading"}
            className="flex-1 focus-visible:ring-2 focus-visible:ring-[oklch(64%_0.18_30)]"
          />
          <Button
            type="submit"
            disabled={status === "loading"}
            className="bg-[oklch(64%_0.18_30)] text-[oklch(98%_0_0)]"
          >
            {status === "loading" ? "..." : cta_text}
          </Button>
        </form>
      )}

      {status === "error" && (
        <p className="mt-2 font-sans text-sm text-[oklch(60%_0.20_25)]" role="alert">
          {error}
        </p>
      )}
    </section>
  )
}
