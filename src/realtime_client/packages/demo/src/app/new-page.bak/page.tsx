import Link from "next/link"

import { siteConfig } from "@/config/site"
import { cn } from "@/lib/utils"
import { buttonVariants } from "@/components/ui/button"
import { Icons } from "@/components/icons"
import { ModeToggle } from "@/components/mode-toggle"

export default function Page() {
  return (
    <main className="flex h-screen items-center justify-center">
      <div className="container flex max-w-[64rem] flex-col items-center gap-4 text-center">
        <h1 className="text-4xl font-semibold sm:text-5xl md:text-6xl lg:text-7xl">
          This is a new page
        </h1>
        <p className="max-w-[42rem] leading-normal text-muted-foreground sm:text-xl sm:leading-8">
          Checkout v0 and the Tailwinds Docs for assistance building a new page
        </p>
        <div className="flex gap-2">
          <Link
            href="https://v0.dev/"
            target="_blank"
            className={cn(buttonVariants({ size: "default" }))}
          >
            v0 AI Assistant
          </Link>
          <Link
            href="https://v3.tailwindcss.com/"
            target="_blank"
            className={cn(buttonVariants({ size: "default" }))}
          >
            Tailwind CSS Docs
          </Link>

          <ModeToggle />
        </div>
      </div>
    </main>
  )
}
