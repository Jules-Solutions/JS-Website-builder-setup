import { Button } from "@/components/ui/button"
import { Check } from "lucide-react"

type Tier = {
  name: string
  price: string
  features: string[]
  cta_text: string
  cta_href: string
}

type PricingTableProps = {
  tiers: Tier[]
  highlight_index?: number
}

export function PricingTable({ tiers, highlight_index = 1 }: PricingTableProps) {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
      {tiers.map((tier, i) => {
        const highlighted = i === highlight_index
        return (
          <div
            key={tier.name}
            className={[
              "flex flex-col rounded-xl border p-6",
              highlighted
                ? "border-[oklch(64%_0.18_30)] ring-1 ring-[oklch(64%_0.18_30)]"
                : "border-[oklch(92%_0_0)]",
            ].join(" ")}
          >
            {highlighted && (
              <span className="mb-3 inline-block rounded-full bg-[oklch(64%_0.18_30)] px-3 py-1 text-xs font-medium text-[oklch(98%_0_0)]">
                Most popular
              </span>
            )}
            <h3 className="font-serif text-xl font-semibold text-[oklch(15%_0_0)]">{tier.name}</h3>
            <p className="mt-2 text-3xl font-bold text-[oklch(15%_0_0)]">{tier.price}</p>
            <ul className="mt-4 flex-1 space-y-2 text-base text-[oklch(15%_0_0)]/80">
              {tier.features.map((f) => (
                <li key={f} className="flex items-start gap-2">
                  <Check className="mt-1 h-4 w-4 text-[oklch(64%_0.18_30)]" aria-hidden="true" />
                  <span>{f}</span>
                </li>
              ))}
            </ul>
            <Button
              asChild
              className="mt-6 bg-[oklch(64%_0.18_30)] text-[oklch(98%_0_0)] focus-visible:ring-2 focus-visible:ring-[oklch(64%_0.18_30)]"
            >
              <a href={tier.cta_href}>{tier.cta_text}</a>
            </Button>
          </div>
        )
      })}
    </div>
  )
}
