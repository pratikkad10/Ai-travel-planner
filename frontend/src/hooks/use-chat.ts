import { useState, useCallback, useEffect, useMemo } from "react"
import type { ChatMessage, TravelSession } from "@/types/travel"
import { sendChatMessage, streamChatMessage, checkHealth } from "@/services/api"

const STORAGE_KEY = "ai_travel_sessions_v1"

function generateThreadId(): string {
  return `trip-${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 7)}`
}

function createWelcomeMessage(): ChatMessage {
  return {
    id: `welcome-${Date.now()}`,
    role: "assistant",
    content:
      "Hello! I am your AI Travel Planner. Tell me where you want to go, your travel dates, budget, or preferences, and I'll calculate costs and build a personalized itinerary for you!",
    timestamp: new Date().toISOString(),
  }
}

function deriveSessionTitle(messages: ChatMessage[]): string {
  const firstUserMsg = messages.find((m) => m.role === "user")
  if (!firstUserMsg || !firstUserMsg.content) return "New Trip"
  const clean = firstUserMsg.content.trim().replace(/\n+/g, " ")
  return clean.length > 30 ? `${clean.substring(0, 30)}...` : clean
}

function loadInitialData(): { sessions: TravelSession[]; activeId: string } {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed: TravelSession[] = JSON.parse(raw)
      if (Array.isArray(parsed) && parsed.length > 0) {
        return { sessions: parsed, activeId: parsed[0].id }
      }
    }
  } catch (e) {
    console.error("Failed to load sessions from localStorage", e)
  }

  const newId = generateThreadId()
  const initialSession: TravelSession = {
    id: newId,
    title: "New Trip",
    createdAt: Date.now(),
    updatedAt: Date.now(),
    messages: [createWelcomeMessage()],
  }
  return { sessions: [initialSession], activeId: newId }
}

export function useChat() {
  const [{ sessions, activeId }, setSessionState] = useState(loadInitialData)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [isBackendOnline, setIsBackendOnline] = useState<boolean | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Persist sessions to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions))
    } catch (e) {
      console.error("Failed to save sessions to localStorage", e)
    }
  }, [sessions])

  // Periodic health check with cold-start tolerance
  useEffect(() => {
    let mounted = true
    let consecutiveFailures = 0

    const verifyHealth = async () => {
      const online = await checkHealth()
      if (!mounted) return

      if (online) {
        consecutiveFailures = 0
        setIsBackendOnline(true)
      } else {
        consecutiveFailures += 1
        // Render free tier can take 30-40s on cold starts.
        // Require 2 consecutive failed health checks before showing "Offline" banner
        if (consecutiveFailures >= 2) {
          setIsBackendOnline(false)
        }
      }
    }

    verifyHealth()
    const interval = setInterval(verifyHealth, 15000)
    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [])

  const activeSession = useMemo(
    () => sessions.find((s) => s.id === activeId) || sessions[0],
    [sessions, activeId]
  )

  const messages = useMemo(
    () => activeSession?.messages || [],
    [activeSession]
  )

  const startNewTrip = useCallback(() => {
    const newId = generateThreadId()
    const newSession: TravelSession = {
      id: newId,
      title: "New Trip",
      createdAt: Date.now(),
      updatedAt: Date.now(),
      messages: [createWelcomeMessage()],
    }
    setSessionState((prev) => ({
      sessions: [newSession, ...prev.sessions],
      activeId: newId,
    }))
    setError(null)
  }, [])

  const switchSession = useCallback((sessionId: string) => {
    setSessionState((prev) => ({ ...prev, activeId: sessionId }))
    setError(null)
  }, [])

  const deleteSession = useCallback((sessionId: string) => {
    setSessionState((prev) => {
      const remaining = prev.sessions.filter((s) => s.id !== sessionId)
      if (remaining.length === 0) {
        const freshId = generateThreadId()
        const freshSession: TravelSession = {
          id: freshId,
          title: "New Trip",
          createdAt: Date.now(),
          updatedAt: Date.now(),
          messages: [createWelcomeMessage()],
        }
        return { sessions: [freshSession], activeId: freshId }
      }
      const nextActiveId =
        prev.activeId === sessionId ? remaining[0].id : prev.activeId
      return { sessions: remaining, activeId: nextActiveId }
    })
  }, [])

  const updateMessages = useCallback(
    (updater: (prev: ChatMessage[]) => ChatMessage[]) => {
      setSessionState((prev) => ({
        ...prev,
        sessions: prev.sessions.map((s) => {
          if (s.id === prev.activeId) {
            const nextMessages = updater(s.messages)
            return {
              ...s,
              messages: nextMessages,
              title:
                s.title === "New Trip"
                  ? deriveSessionTitle(nextMessages)
                  : s.title,
              updatedAt: Date.now(),
            }
          }
          return s
        }),
      }))
    },
    []
  )

  const sendMessage = useCallback(
    async (userText: string) => {
      const trimmed = userText.trim()
      if (!trimmed || isLoading) return

      const currentThreadId = activeId
      const userMsgId = `user-${Date.now()}`
      const assistantMsgId = `assistant-${Date.now()}`

      const userMsg: ChatMessage = {
        id: userMsgId,
        role: "user",
        content: trimmed,
        timestamp: new Date().toISOString(),
      }

      const assistantMsg: ChatMessage = {
        id: assistantMsgId,
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
        isStreaming: true,
      }

      updateMessages((prev) => [...prev, userMsg, assistantMsg])
      setIsLoading(true)
      setError(null)

      try {
        let accumulatedText = ""
        try {
          await streamChatMessage(
            { message: trimmed, thread_id: currentThreadId },
            (chunk: string) => {
              accumulatedText += chunk
              updateMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsgId
                    ? { ...m, content: accumulatedText, isStreaming: true }
                    : m
                )
              )
            }
          )
        } catch {
          const fallbackRes = await sendChatMessage({
            message: trimmed,
            thread_id: currentThreadId,
          })
          accumulatedText = fallbackRes.response
        }

        updateMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsgId
              ? {
                  ...m,
                  content:
                    accumulatedText ||
                    "I received your request but didn't get any text response. Please try again.",
                  isStreaming: false,
                }
              : m
          )
        )
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to communicate with AI service"
        setError(message)
        updateMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsgId
              ? {
                  ...m,
                  content: `⚠️ Error: ${message}. Ensure backend is running at http://localhost:8000.`,
                  isStreaming: false,
                }
              : m
          )
        )
      } finally {
        setIsLoading(false)
      }
    },
    [activeId, isLoading, updateMessages]
  )

  return {
    messages,
    threadId: activeId,
    sessions,
    isLoading,
    isBackendOnline,
    error,
    sendMessage,
    startNewTrip,
    switchSession,
    deleteSession,
  }
}
