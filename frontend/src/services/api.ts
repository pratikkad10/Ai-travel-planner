import type { ChatRequest, ChatResponse } from "@/types/travel"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`)
    return res.ok
  } catch {
    return false
  }
}

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  })

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || `Server error: ${res.status}`)
  }

  return res.json()
}

export async function streamChatMessage(
  request: ChatRequest,
  onChunk: (chunk: string) => void
): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  })

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || `Streaming error: ${res.status}`)
  }

  const reader = res.body?.getReader()
  if (!reader) {
    throw new Error("Response body is not readable")
  }

  const decoder = new TextDecoder()
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    const chunk = decoder.decode(value, { stream: true })
    if (chunk) {
      onChunk(chunk)
    }
  }
}
