import { useEffect } from "react"
import { Plus, Trash2, X, Compass, Clock } from "lucide-react"
import type { TravelSession } from "@/types/travel"

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
  sessions: TravelSession[]
  activeSessionId: string
  onSelectSession: (id: string) => void
  onDeleteSession: (id: string) => void
  onNewTrip: () => void
}

function formatRelativeTime(timestamp: number): string {
  const diff = Date.now() - timestamp
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return "Just now"
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  return new Date(timestamp).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  })
}

export function Sidebar({
  isOpen,
  onClose,
  sessions,
  activeSessionId,
  onSelectSession,
  onDeleteSession,
  onNewTrip,
}: SidebarProps) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose()
      }
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [isOpen, onClose])

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-30 bg-slate-900/20 backdrop-blur-xs transition-opacity lg:hidden"
          aria-hidden="true"
        />
      )}

      {/* Sidebar Panel */}
      <aside
        aria-hidden={!isOpen}
        aria-label="Trip history sidebar"
        className={`fixed inset-y-0 left-0 z-40 flex w-72 sm:w-80 flex-col border-r border-slate-200/90 bg-white shadow-lg transition-transform duration-200 ease-in-out dark:border-[#282828] dark:bg-[#121212] lg:static lg:z-auto lg:shadow-none ${
          isOpen
            ? "translate-x-0 pointer-events-auto"
            : "-translate-x-full pointer-events-none lg:hidden"
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 p-4 dark:border-[#282828]">
          <div className="flex items-center gap-2 text-slate-800 dark:text-white">
            <Compass className="h-4 w-4 text-zinc-800 dark:text-zinc-200" />
            <span className="text-sm font-semibold">Trip History</span>
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-500 dark:bg-[#242424] dark:text-zinc-300">
              {sessions.length}
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close sidebar"
            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-[#242424] dark:hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* New Trip Action */}
        <div className="p-3">
          <button
            type="button"
            onClick={() => {
              onNewTrip()
              if (window.innerWidth < 1024) onClose()
            }}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-slate-300 bg-slate-50/70 px-3 py-2.5 text-xs font-medium text-slate-700 transition hover:border-slate-400 hover:bg-slate-100 hover:text-slate-900 active:scale-[0.99] dark:border-[#2e2e2e] dark:bg-[#181818] dark:text-zinc-200 dark:hover:border-[#3e3e3e] dark:hover:bg-[#242424] dark:hover:text-white"
          >
            <Plus className="h-4 w-4 text-zinc-800 dark:text-zinc-200" />
            <span>Start New Trip</span>
          </button>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto px-3 py-1 space-y-1">
          {sessions.length === 0 ? (
            <div className="flex h-32 flex-col items-center justify-center text-center text-xs text-slate-400 dark:text-zinc-500">
              <Clock className="mb-2 h-6 w-6 text-slate-300 dark:text-zinc-600" />
              <span>No trips saved yet</span>
            </div>
          ) : (
            sessions.map((session) => {
              const isActive = session.id === activeSessionId
              return (
                <div
                  key={session.id}
                  onClick={() => {
                    onSelectSession(session.id)
                    if (window.innerWidth < 1024) onClose()
                  }}
                  className={`group relative flex cursor-pointer items-center justify-between rounded-xl px-3 py-2.5 text-xs transition-all ${
                    isActive
                      ? "bg-slate-100 font-semibold text-slate-900 shadow-2xs dark:bg-[#242424] dark:text-white"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:text-zinc-400 dark:hover:bg-[#181818] dark:hover:text-zinc-200"
                  }`}
                >
                  <div className="min-w-0 flex-1 pr-2">
                    <p className="truncate text-xs font-medium leading-tight">
                      {session.title || "Untitled Trip"}
                    </p>
                    <span className="text-[10px] text-slate-400 dark:text-zinc-500">
                      {formatRelativeTime(session.updatedAt)}
                    </span>
                  </div>

                  {/* Delete Button */}
                  <button
                    type="button"
                    title="Delete trip"
                    aria-label={`Delete ${session.title}`}
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteSession(session.id)
                    }}
                    className="rounded-md p-1 text-slate-400 opacity-0 transition hover:bg-rose-50 hover:text-rose-600 group-hover:opacity-100 dark:hover:bg-rose-950/40 dark:hover:text-rose-400"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              )
            })
          )}
        </div>

        {/* Footer info */}
        <div className="border-t border-slate-100 p-3 text-center dark:border-[#282828]">
          <p className="text-[10px] text-slate-400 dark:text-zinc-500">
            Sessions saved locally in browser
          </p>
        </div>
      </aside>
    </>
  )
}
