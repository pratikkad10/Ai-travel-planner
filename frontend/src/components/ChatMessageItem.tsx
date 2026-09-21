import { useState, useMemo } from "react"
import { Bot, User, Copy, Check } from "lucide-react"
import type { ChatMessage } from "@/types/travel"

interface ChatMessageItemProps {
  message: ChatMessage
}

export function ChatMessageItem({ message }: ChatMessageItemProps) {
  const [copied, setCopied] = useState(false)
  const isUser = message.role === "user"

  const handleCopy = async () => {
    if (!message.content) return
    await navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Basic markdown-like rendering for headers, lists, and bold text
  const renderedContent = useMemo(() => {
    if (!message.content) {
      if (message.isStreaming) {
        return (
          <div className="flex items-center gap-1.5 py-1 text-slate-400">
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.3s]" />
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.15s]" />
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" />
            <span className="ml-2 text-xs">Researching & calculating...</span>
          </div>
        )
      }
      return null
    }

    const lines = message.content.split("\n")
    const elements: React.ReactNode[] = []
    let idx = 0

    while (idx < lines.length) {
      const line = lines[idx]
      const trimmed = line.trim()

      // Table parsing: lines starting and ending with '|'
      if (trimmed.startsWith("|") && trimmed.endsWith("|")) {
        const tableLines: string[] = []
        const startIdx = idx
        while (
          idx < lines.length &&
          lines[idx].trim().startsWith("|") &&
          lines[idx].trim().endsWith("|")
        ) {
          tableLines.push(lines[idx].trim())
          idx++
        }

        if (tableLines.length >= 2) {
          const parseRow = (r: string) =>
            r
              .split("|")
              .slice(1, -1)
              .map((c) => c.trim())

          const headers = parseRow(tableLines[0])
          const isDivider = /^(\|\s*[-:]+\s*)+\|$/.test(tableLines[1])
          const dataRows = tableLines
            .slice(isDivider ? 2 : 1)
            .map(parseRow)

          elements.push(
            <div
              key={`table-${startIdx}`}
              className="my-3 w-full overflow-x-auto rounded-xl border border-slate-200/90 bg-white shadow-2xs dark:border-[#282828] dark:bg-[#181818]"
            >
              <table className="w-full text-left text-xs">
                <thead className="border-b border-slate-200 bg-slate-50/80 font-semibold text-slate-800 dark:border-[#282828] dark:bg-[#202020] dark:text-zinc-200">
                  <tr>
                    {headers.map((h, hi) => (
                      <th key={hi} className="px-3.5 py-2.5">
                        {renderFormattedInline(h, isUser)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700 dark:divide-[#282828] dark:text-zinc-300">
                  {dataRows.map((row, ri) => (
                    <tr key={ri} className="transition-colors hover:bg-slate-50/50 dark:hover:bg-[#222222]">
                      {row.map((cell, ci) => (
                        <td key={ci} className="px-3.5 py-2.5">
                          {renderFormattedInline(cell, isUser)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
          continue
        }
      }

      // 1. Horizontal Rule: ---, ***, ___
      if (/^(\-{3,}|\*{3,}|_{3,})$/.test(trimmed)) {
        elements.push(<hr key={`hr-${idx}`} className="my-3 border-slate-200/80 dark:border-[#282828]" />)
        idx++
        continue
      }

      // 2. Headings: #, ##, ###, ####, #####, ######
      const headingMatch = trimmed.match(/^(#{1,6})\s+(.*)$/)
      if (headingMatch) {
        const level = headingMatch[1].length
        const headingText = headingMatch[2]

        if (level === 1) {
          elements.push(
            <h1
              key={`h1-${idx}`}
              className="mt-4 mb-2 text-lg font-bold tracking-tight text-slate-950 dark:text-white first:mt-0"
            >
              {renderFormattedInline(headingText, isUser)}
            </h1>
          )
        } else if (level === 2) {
          elements.push(
            <h2
              key={`h2-${idx}`}
              className="mt-3.5 mb-1.5 text-base font-bold tracking-tight text-slate-900 dark:text-white first:mt-0"
            >
              {renderFormattedInline(headingText, isUser)}
            </h2>
          )
        } else if (level === 3) {
          elements.push(
            <h3
              key={`h3-${idx}`}
              className="mt-3 mb-1 text-sm font-semibold text-slate-900 dark:text-white first:mt-0"
            >
              {renderFormattedInline(headingText, isUser)}
            </h3>
          )
        } else {
          elements.push(
            <h4
              key={`h4-${idx}`}
              className="mt-2.5 mb-1 text-xs font-semibold tracking-wide uppercase text-slate-600 dark:text-zinc-400 first:mt-0"
            >
              {renderFormattedInline(headingText, isUser)}
            </h4>
          )
        }
        idx++
        continue
      }

      // 3. Standalone bold headers: e.g. **Assumptions:**, **Calculations:**, **3. Convert to INR:**
      const standaloneBoldMatch = trimmed.match(/^\*\*(.*?)\*\*$/)
      if (standaloneBoldMatch) {
        elements.push(
          <h3
            key={`sb-${idx}`}
            className="mt-3 mb-1 text-sm font-semibold text-slate-900 dark:text-white first:mt-0"
          >
            {standaloneBoldMatch[1]}
          </h3>
        )
        idx++
        continue
      }

      // 4. Bullet lists: -, *, +, •
      const bulletMatch = trimmed.match(/^([-*+•]|\u2022)\s*(.*)$/)
      if (bulletMatch) {
        elements.push(
          <li
            key={`li-${idx}`}
            className={`ml-4 list-disc text-sm leading-relaxed marker:text-slate-400 dark:marker:text-zinc-500 ${
              isUser ? "text-slate-900 dark:text-white" : "text-slate-700 dark:text-zinc-300"
            }`}
          >
            {renderFormattedInline(bulletMatch[2], isUser)}
          </li>
        )
        idx++
        continue
      }

      // 5. Numbered lists: 1. , 2. , etc.
      const numberedMatch = trimmed.match(/^(\d+)\.\s+(.*)$/)
      if (numberedMatch) {
        elements.push(
          <div
            key={`num-${idx}`}
            className={`ml-1 flex items-start gap-2 text-sm leading-relaxed ${
              isUser ? "text-slate-900 dark:text-white" : "text-slate-700 dark:text-zinc-300"
            }`}
          >
            <span className="shrink-0 font-semibold text-slate-500 dark:text-zinc-400">
              {numberedMatch[1]}.
            </span>
            <div className="flex-1">
              {renderFormattedInline(numberedMatch[2], isUser)}
            </div>
          </div>
        )
        idx++
        continue
      }

      // 6. Empty lines
      if (!trimmed) {
        elements.push(<div key={`empty-${idx}`} className="h-2" />)
        idx++
        continue
      }

      // 7. Standard paragraph
      elements.push(
        <p
          key={`p-${idx}`}
          className={`text-sm leading-relaxed ${
            isUser
              ? "text-slate-900 dark:text-white"
              : "text-slate-800 dark:text-zinc-200"
          }`}
        >
          {renderFormattedInline(line, isUser)}
        </p>
      )
      idx++
    }

    return elements
  }, [message.content, message.isStreaming, isUser])

  return (
    <div
      className={`flex w-full gap-3 ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      {/* Assistant avatar */}
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-900 text-white shadow-xs dark:border dark:border-[#333333] dark:bg-[#242424] dark:text-zinc-200">
          <Bot className="h-4 w-4" />
        </div>
      )}

      {/* Message bubble */}
      <div
        className={`group relative transition-all ${
          isUser
            ? "max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-tr-xs bg-slate-100/90 border border-slate-200/90 text-slate-900 shadow-2xs px-4 py-3 dark:border-[#333333] dark:bg-[#282828] dark:text-white"
            : "w-full flex-1 rounded-2xl rounded-tl-xs border border-slate-200/80 bg-white text-slate-800 shadow-xs p-4 sm:p-5 dark:border-[#282828] dark:bg-[#181818] dark:text-zinc-200"
        }`}
      >
        <div className="space-y-1">{renderedContent}</div>

        {/* Copy button for assistant responses */}
        {!isUser && message.content && (
          <button
            type="button"
            onClick={handleCopy}
            aria-label="Copy response"
            className="absolute top-2.5 right-2.5 rounded-md p-1 text-slate-400 opacity-0 transition hover:bg-slate-100 hover:text-slate-600 group-hover:opacity-100 dark:hover:bg-[#282828] dark:hover:text-zinc-200"
          >
            {copied ? (
              <Check className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
            ) : (
              <Copy className="h-3.5 w-3.5" />
            )}
          </button>
        )}
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-700 shadow-2xs dark:border-[#333333] dark:bg-[#282828] dark:text-zinc-200">
          <User className="h-4 w-4" />
        </div>
      )}
    </div>
  )
}

function renderFormattedInline(text: string, isUser: boolean = false) {
  // Matches: `code`, ***bold-italic***, **bold**, *italic*
  const tokenRegex = /(`[^`]+`|\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|\*[^*]+\*)/g
  const parts = text.split(tokenRegex)

  return parts.map((part, i) => {
    if (!part) return null

    // Inline Code: `code`
    if (part.startsWith("`") && part.endsWith("`") && part.length >= 2) {
      return (
        <code
          key={i}
          className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-xs font-medium text-slate-800 border border-slate-200/80 dark:border-[#333333] dark:bg-[#242424] dark:text-zinc-200"
        >
          {part.slice(1, -1)}
        </code>
      )
    }

    // Bold + Italic: ***text***
    if (part.startsWith("***") && part.endsWith("***") && part.length >= 6) {
      return (
        <strong
          key={i}
          className={`font-semibold italic ${
            isUser ? "text-slate-950 dark:text-white" : "text-slate-900 dark:text-white"
          }`}
        >
          {part.slice(3, -3)}
        </strong>
      )
    }

    // Bold: **text**
    if (part.startsWith("**") && part.endsWith("**") && part.length >= 4) {
      return (
        <strong
          key={i}
          className={`font-semibold ${
            isUser ? "text-slate-950 dark:text-white" : "text-slate-900 dark:text-white"
          }`}
        >
          {part.slice(2, -2)}
        </strong>
      )
    }

    // Italic: *text*
    if (part.startsWith("*") && part.endsWith("*") && part.length >= 2) {
      return (
        <em
          key={i}
          className={`italic ${
            isUser ? "text-slate-800 dark:text-zinc-200" : "text-slate-800 dark:text-zinc-300"
          }`}
        >
          {part.slice(1, -1)}
        </em>
      )
    }

    return part
  })
}
