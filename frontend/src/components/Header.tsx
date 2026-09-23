import { Compass, Plus, PanelLeft, Sun, Moon, Menu } from "lucide-react"

interface HeaderProps {
  isSidebarOpen?: boolean
  theme: "light" | "dark"
  onToggleTheme: () => void
  onNewTrip: () => void
  onToggleSidebar: () => void
  threadId: string
}

export function Header({
  isSidebarOpen,
  theme,
  onToggleTheme,
  onNewTrip,
  onToggleSidebar,
  threadId,
}: HeaderProps) {
  return (
    <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/95 px-4 py-3 backdrop-blur-md dark:border-[#282828] dark:bg-[#121212]/95 sm:px-6">
      <div className="flex w-full items-center justify-between">
        {/* Left: Sidebar toggle + Brand */}
        <div className="flex items-center gap-2 sm:gap-3">
          <button
            type="button"
            onClick={onToggleSidebar}
            aria-label={isSidebarOpen ? "Close trip history sidebar" : "Open trip history sidebar"}
            aria-expanded={isSidebarOpen}
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 shadow-2xs transition hover:bg-slate-50 hover:text-slate-900 active:scale-95 dark:border-[#282828] dark:bg-[#242424] dark:text-zinc-300 dark:hover:bg-[#2e2e2e] dark:hover:text-white"
            title={isSidebarOpen ? "Close sidebar" : "Open sidebar"}
          >
            <Menu className="h-4.5 w-4.5 lg:hidden" />
            <PanelLeft className="hidden h-4 w-4 lg:block" />
          </button>

          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-900 text-white shadow-2xs dark:bg-[#242424] dark:text-white">
            <Compass className="h-4 w-4" />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-semibold text-slate-900 dark:text-white sm:text-base">
                AI Travel Planner
              </h1>
              <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600 dark:bg-[#242424] dark:text-zinc-300 sm:text-[11px]">
                Agent
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-zinc-400">
              Session:{" "}
              <span className="font-mono text-slate-700 dark:text-zinc-300">
                {threadId.slice(0, 12)}...
              </span>
            </p>
          </div>
        </div>

        {/* Right: Theme Toggle & New trip */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Theme Toggle Button */}
          <button
            type="button"
            onClick={onToggleTheme}
            aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
            title={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
            className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white p-2 text-slate-600 shadow-2xs transition-all duration-300 hover:bg-slate-50 hover:text-slate-900 active:scale-95 dark:border-[#282828] dark:bg-[#242424] dark:text-zinc-300 dark:hover:bg-[#2e2e2e] dark:hover:text-white"
          >
            <div className="relative h-4 w-4">
              <Sun
                className={`absolute inset-0 h-4 w-4 text-amber-400 transition-all duration-300 ease-out ${
                  theme === "dark"
                    ? "rotate-0 scale-100 opacity-100"
                    : "-rotate-90 scale-0 opacity-0"
                }`}
              />
              <Moon
                className={`absolute inset-0 h-4 w-4 text-slate-600 transition-all duration-300 ease-out dark:text-zinc-300 ${
                  theme === "light"
                    ? "rotate-0 scale-100 opacity-100"
                    : "rotate-90 scale-0 opacity-0"
                }`}
              />
            </div>
          </button>

          {/* New Trip Button */}
          <button
            type="button"
            onClick={onNewTrip}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 shadow-2xs transition hover:bg-slate-50 hover:text-slate-900 active:scale-95 dark:border-[#282828] dark:bg-[#242424] dark:text-zinc-200 dark:hover:bg-[#2e2e2e] dark:hover:text-white"
            aria-label="Start new trip"
          >
            <Plus className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">New Trip</span>
          </button>
        </div>
      </div>
    </header>
  )
}
