import Link from "next/link"
import { ArrowRight } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

type FeatureCardProps = {
  icon: React.ReactNode
  title: string
  body: string
  href?: string
}

export function FeatureCard({ icon, title, body, href }: FeatureCardProps) {
  const content = (
    <Card className="h-full bg-card transition-shadow duration-150 hover:shadow-md focus-visible:ring-2 focus-visible:ring-primary">
      <CardContent className="flex flex-col gap-3 p-6">
        <div className="text-primary" aria-hidden="true">
          {icon}
        </div>
        <h3 className="font-serif text-xl font-semibold text-foreground">{title}</h3>
        <p className="font-sans text-base leading-relaxed text-muted-foreground">{body}</p>
        {href && (
          <span className="mt-2 inline-flex items-center gap-1 text-primary">
            Learn more <ArrowRight className="h-4 w-4" />
          </span>
        )}
      </CardContent>
    </Card>
  )

  if (href) {
    return (
      <Link href={href} className="block focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-lg">
        {content}
      </Link>
    )
  }
  return content
}
