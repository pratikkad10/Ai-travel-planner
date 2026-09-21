import { useEffect, useRef } from "react"
import type { ChatMessage } from "@/types/travel"
import { ChatMessageItem } from "./ChatMessageItem"

interface ChatListProps {
  messages: ChatMessage[]
}

export function ChatList({ messages }: ChatListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  return (
    <div className="flex flex-1 flex-col space-y-6 overflow-y-auto px-4 py-6 sm:px-6">
      <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col space-y-5">
        {messages.map((message) => (
          <ChatMessageItem key={message.id} message={message} />
        ))}
        <div ref={bottomRef} className="h-2 shrink-0" />
      </div>
    </div>
  )
}
