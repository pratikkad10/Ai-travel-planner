from typing import Optional, Any, Dict
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser

from agent import agent

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
    allow_origins=["*"],
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


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": request.message,
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
        async def event_generator():
            async for event in agent.astream_events(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": request.message,
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
                        # Use StrOutputParser to parse streaming chunks properly
                        text = str_output_parser.invoke(chunk)
                        if text:
                            yield text

        return StreamingResponse(event_generator(), media_type="text/plain")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
