import { Sparkles, MapPin, DollarSign, Calendar } from "lucide-react"
import type { QuickPromptItem } from "@/types/travel"

interface QuickPromptsProps {
  onSelectPrompt: (prompt: string) => void
  disabled?: boolean
}

const SAMPLE_PROMPTS: QuickPromptItem[] = [
  {
    id: "japan-budget",
    title: "Japan 7-Day Budget",
    tag: "Budget & Currency",
    prompt:
      "I'm going to Japan for 7 days. My hotel costs ¥12,000 per night, food costs ¥4,000 per day, and transportation will cost ¥2,000 per day. My home currency is INR. Calculate my total budget.",
  },
  {
    id: "goa-getaway",
    title: "Goa 4-Day Trip",
    tag: "Beach & Flights",
    prompt:
      "Find flights from BOM to GOI and plan a 4-day beach vacation in Goa with hotel options, food spots, and attractions.",
  },
  {
    id: "paris-itinerary",
    title: "Paris 5 Days",
    tag: "Sightseeing & Weather",
    prompt:
      "Plan a 5-day trip to Paris with top attractions, check current weather, and calculate an estimated budget in INR.",
  },
]

export function QuickPrompts({ onSelectPrompt, disabled }: QuickPromptsProps) {
  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-2 sm:px-6">
      <div className="mb-2 flex items-center gap-1.5 text-xs font-medium text-slate-500 dark:text-zinc-400">
        <Sparkles className="h-3.5 w-3.5 text-zinc-700 dark:text-zinc-300" />
        <span>Quick Trip Ideas</span>
      </div>
      <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-3">
        {SAMPLE_PROMPTS.map((item) => (
          <button
            key={item.id}
            type="button"
            disabled={disabled}
            onClick={() => onSelectPrompt(item.prompt)}
            className="flex flex-col items-start rounded-xl border border-slate-200/80 bg-white p-3 text-left shadow-2xs transition hover:border-slate-300 hover:bg-slate-50/80 active:scale-[0.98] disabled:pointer-events-none disabled:opacity-50 dark:border-[#282828] dark:bg-[#181818] dark:hover:border-[#383838] dark:hover:bg-[#242424]"
          >
            <div className="mb-1 flex w-full items-center justify-between">
              <span className="text-xs font-semibold text-slate-800 dark:text-white">
                {item.title}
              </span>
              {item.id === "japan-budget" ? (
                <DollarSign className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
              ) : item.id === "goa-getaway" ? (
                <MapPin className="h-3.5 w-3.5 text-amber-500 dark:text-amber-400" />
              ) : (
                <Calendar className="h-3.5 w-3.5 text-zinc-600 dark:text-zinc-400" />
              )}
            </div>
            <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-500 dark:bg-[#242424] dark:text-zinc-400">
              {item.tag}
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}
