Here's your HeroBlock component:

```tsx
import { Button } from "@/components/ui/button"

type HeroBlockProps = {
  headline: string
  sub: string
  cta_text: string
  background_image?: string
}

export function HeroBlock({ headline, sub, cta_text, background_image }: HeroBlockProps) {
  return (
    <section className="relative min-h-screen flex items-center justify-center px-4 lg:px-16">
      {background_image && (
        <img
          src={background_image}
          alt=""
          className="absolute inset-0 w-full h-full object-cover -z-10"
        />
      )}
      <div className="max-w-4xl text-center">
        <h1 className="font-serif text-5xl md:text-7xl font-bold leading-tight">
          {headline}
        </h1>
        <p className="mt-6 text-lg md:text-xl">{sub}</p>
        <Button className="mt-8 bg-indigo-600 hover:bg-indigo-700" size="lg">
          {cta_text}
        </Button>
      </div>
    </section>
  )
}
```

Let me know if you'd like a dark-mode variant!
