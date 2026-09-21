export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: string | Date
  isStreaming?: boolean
}

export interface ChatRequest {
  message: string
  thread_id?: string
}

export interface ChatResponse {
  response: string
  thread_id: string
}

export interface QuickPromptItem {
  id: string
  title: string
  prompt: string
  tag: string
}

export interface TravelSession {
  id: string
  title: string
  createdAt: number
  updatedAt: number
  messages: ChatMessage[]
}

