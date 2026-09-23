from typing import Optional, Any, Dict
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser

from agent import agent
from agent.query_optimizer import optimize_user_query
from langchain_core.messages import HumanMessage, AIMessage

app = FastAPI(
    title="AI Travel Planner API",
    description="FastAPI service for the AI Travel Planner LangGraph Agent",
    version="1.0.0",
)

# Output parser instance for extracting string content from agent messages/chunks
str_output_parser = StrOutputParser()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://ai-travel-planner-xi-rust.vercel.app",
        "https://ai-travel-planner-kvfap6sf9-pratikkad10s-projects.vercel.app"
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., description="User query or input for the travel planner")
    thread_id: Optional[str] = Field(
        default="travel-session-default",
        description="Session identifier to preserve conversational memory across requests",
    )


class BudgetDetails(BaseModel):
    flight: Optional[float] = Field(default=None, description="Estimated flight cost")
    hotel: Optional[float] = Field(default=None, description="Estimated hotel/stay cost")
    food: Optional[float] = Field(default=None, description="Estimated food & dining cost")
    transport: Optional[float] = Field(default=None, description="Estimated local transport cost")
    activities: Optional[float] = Field(default=None, description="Estimated activities cost")
    miscellaneous: Optional[float] = Field(default=None, description="Estimated miscellaneous cost")
    total: Optional[float] = Field(default=None, description="Total budget")
    currency: Optional[str] = Field(default="INR", description="Currency code or symbol")


class ChatResponse(BaseModel):
    response: str
    thread_id: str


def get_thread_history(thread_id: str, limit: int = 6) -> str:
    """Retrieve recent conversation history from the agent's checkpointer."""
    try:
        state = agent.get_state({"configurable": {"thread_id": thread_id}})
        if state and state.values and "messages" in state.values:
            recent_msgs = state.values["messages"][-limit:]
            formatted = []
            for msg in recent_msgs:
                role = getattr(msg, "type", "message")
                content = getattr(msg, "content", "")
                if isinstance(content, str) and content.strip():
                    formatted.append(f"{role}: {content.strip()}")
            return "\n".join(formatted)
    except Exception as e:
        print(f"Could not load thread history: {e}")
    return ""


def record_clarification_turn(thread_id: str, user_text: str, clarification: str) -> None:
    """Record user input and assistant clarification question into agent checkpointer state."""
    try:
        agent.update_state(
            {"configurable": {"thread_id": thread_id}},
            {"messages": [HumanMessage(content=user_text), AIMessage(content=clarification)]},
        )
    except Exception as e:
        print(f"Could not record clarification turn: {e}")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. Fetch recent history for conversational context
        history_str = get_thread_history(request.thread_id)

        # 2. Optimize user query using LLM
        effective_message = request.message
        try:
            intent = optimize_user_query(request.message, history=history_str)

            # If critical info (e.g. origin city for flights) is missing, ask for clarification
            if intent.needs_clarification and intent.clarification_question:
                record_clarification_turn(
                    request.thread_id, request.message, intent.clarification_question
                )
                return ChatResponse(
                    response=intent.clarification_question,
                    thread_id=request.thread_id,
                )

            if intent.optimized_prompt:
                effective_message = intent.optimized_prompt
        except Exception as opt_err:
            print(f"Query optimization skipped due to error: {opt_err}")
            effective_message = request.message

        # 3. Invoke agent with optimized query
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": effective_message,
                    }
                ]
            },
            {
                "configurable": {
                    "thread_id": request.thread_id,
                }
            },
        )

        # Use LangChain's StrOutputParser to properly parse the final AIMessage
        agent_content = str_output_parser.invoke(result["messages"][-1])

        return ChatResponse(
            response=agent_content,
            thread_id=request.thread_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    try:
        # 1. Fetch recent history for conversational context
        history_str = get_thread_history(request.thread_id)

        # 2. Optimize user query using LLM
        effective_message = request.message
        clarification_response: Optional[str] = None

        try:
            intent = optimize_user_query(request.message, history=history_str)

            if intent.needs_clarification and intent.clarification_question:
                clarification_response = intent.clarification_question
                record_clarification_turn(
                    request.thread_id, request.message, clarification_response
                )
            elif intent.optimized_prompt:
                effective_message = intent.optimized_prompt
        except Exception as opt_err:
            print(f"Query optimization skipped due to error: {opt_err}")
            effective_message = request.message

        # If a clarification is needed, stream it directly
        if clarification_response:
            async def clarification_generator():
                yield clarification_response

            return StreamingResponse(clarification_generator(), media_type="text/plain")

        # 3. Stream agent response with optimized query
        async def event_generator():
            async for event in agent.astream_events(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": effective_message,
                        }
                    ]
                },
                {
                    "configurable": {
                        "thread_id": request.thread_id,
                    }
                },
                version="v2",
            ):
                if event.get("event") == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk:
                        text = str_output_parser.invoke(chunk)
                        if text:
                            yield text

        return StreamingResponse(event_generator(), media_type="text/plain")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

