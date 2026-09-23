import { useState, useEffect } from "react"
import { WifiOff } from "lucide-react"
import { useChat } from "@/hooks/use-chat"
import { Header } from "@/components/Header"
import { Sidebar } from "@/components/Sidebar"
import { ChatList } from "@/components/ChatList"
import { QuickPrompts } from "@/components/QuickPrompts"
import { ChatInput } from "@/components/ChatInput"

export function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(() => {
    if (typeof window !== "undefined") {
      return window.innerWidth >= 1024
    }
    return false
  })

  // Synchronize sidebar default state if screen resizes across the mobile/desktop breakpoint
  useEffect(() => {
    if (typeof window === "undefined") return

    const mediaQuery = window.matchMedia("(min-width: 1024px)")
    const handleMediaChange = (e: MediaQueryListEvent) => {
      setIsSidebarOpen(e.matches)
    }

    mediaQuery.addEventListener("change", handleMediaChange)
    return () => mediaQuery.removeEventListener("change", handleMediaChange)
  }, [])

  const [theme, setTheme] = useState<"light" | "dark">(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("travel_planner_theme")
      if (saved === "dark" || saved === "light") return saved
      return window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light"
    }
    return "light"
  })

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
    localStorage.setItem("travel_planner_theme", theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"))
  }

  const {
    messages,
    threadId,
    sessions,
    isLoading,
    isBackendOnline,
    sendMessage,
    startNewTrip,
    switchSession,
    deleteSession,
  } = useChat()

  const showQuickPrompts = messages.length <= 1

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 antialiased overflow-hidden dark:bg-[#121212] dark:text-zinc-100">
      {/* Sessions Sidebar */}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        sessions={sessions}
        activeSessionId={threadId}
        onSelectSession={switchSession}
        onDeleteSession={deleteSession}
        onNewTrip={startNewTrip}
      />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Navigation */}
        <Header
          isSidebarOpen={isSidebarOpen}
          theme={theme}
          onToggleTheme={toggleTheme}
          onNewTrip={startNewTrip}
          onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
          threadId={threadId}
        />

        {/* Conversation Stream */}
        <main className="flex flex-1 flex-col overflow-hidden">
          <ChatList messages={messages} />

          {/* Quick Prompts */}
          {showQuickPrompts && (
            <div className="pb-2">
              <QuickPrompts onSelectPrompt={sendMessage} disabled={isLoading} />
            </div>
          )}

          {/* Bottom Chat Input */}
          <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
        </main>
      </div>

      {/* Offline Toast Notification */}
      {isBackendOnline === false && (
        <div
          role="alert"
          className="fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-2xl border border-rose-200 bg-white/95 px-4 py-3 text-sm text-slate-800 shadow-xl backdrop-blur-md dark:border-rose-900/40 dark:bg-[#181818]/95 dark:text-zinc-200"
        >
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-rose-50 text-rose-600 dark:bg-rose-950/40 dark:text-rose-400">
            <WifiOff className="h-4 w-4" />
          </div>
          <div>
            <p className="text-xs font-semibold text-rose-900 dark:text-rose-300">
              Service Offline
            </p>
            <p className="text-[11px] text-slate-500 dark:text-zinc-400">
              AI backend is unreachable. Please check connection.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
