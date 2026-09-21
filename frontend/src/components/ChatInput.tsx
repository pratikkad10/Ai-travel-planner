import { useState, useRef, type KeyboardEvent, type ChangeEvent } from "react"
import { ArrowUp, Loader2 } from "lucide-react"

interface ChatInputProps {
  onSendMessage: (message: string) => void
  isLoading: boolean
}

export function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [text, setText] = useState("")
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleSubmit = () => {
    const trimmed = text.trim()
    if (!trimmed || isLoading) return
    onSendMessage(trimmed)
    setText("")
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
    }
  }

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value)
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        140
      )}px`
    }
  }

  return (
    <div className="border-t border-slate-200 bg-white/95 px-4 py-3 backdrop-blur-md dark:border-[#282828] dark:bg-[#121212]/95 sm:px-6">
      <div className="mx-auto max-w-3xl">
        <div className="relative flex items-end rounded-2xl border border-slate-300/80 bg-white p-2 shadow-xs transition-within focus-within:border-slate-800 focus-within:ring-1 focus-within:ring-slate-800 dark:border-[#282828] dark:bg-[#181818] dark:focus-within:border-[#404040] dark:focus-within:ring-[#404040]">
          <textarea
            ref={textareaRef}
            rows={1}
            value={text}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder="Ask anything (e.g. 7 days in Japan with ¥12,000 hotel/night in INR)..."
            className="max-h-36 min-h-10 flex-1 resize-none bg-transparent px-2 py-1.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-hidden disabled:opacity-50 dark:text-white dark:placeholder:text-zinc-500"
            aria-label="Travel plan input"
          />

          <button
            type="button"
            onClick={handleSubmit}
            disabled={!text.trim() || isLoading}
            aria-label="Send message"
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white transition hover:bg-slate-800 active:scale-95 disabled:pointer-events-none disabled:opacity-40 dark:bg-white dark:text-black dark:hover:bg-zinc-200"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <ArrowUp className="h-4 w-4" />
            )}
          </button>
        </div>

        <p className="mt-2 text-center text-[11px] text-slate-400 dark:text-zinc-500">
          Your smart travel companion for flights, hotels, weather, and budget planning.
        </p>
      </div>
    </div>
  )
}
