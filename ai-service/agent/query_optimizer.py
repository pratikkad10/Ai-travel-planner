from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

class ExtractedTravelIntent(BaseModel):
    is_travel_query: bool = Field(description="Whether the query is related to travel planning")
    origin_city: Optional[str] = Field(default=None, description="Departure city in plain English (e.g., Mumbai)")
    destination_city: Optional[str] = Field(default=None, description="Arrival city in plain English (e.g., Goa)")
    departure_date: Optional[str] = Field(default=None, description="Departure date in YYYY-MM-DD format (must be future)")
    return_date: Optional[str] = Field(default=None, description="Return date in YYYY-MM-DD format if mentioned")
    adults: Optional[int] = Field(default=1, description="Number of travelers")
    budget: Optional[float] = Field(default=None, description="Budget amount")
    currency: Optional[str] = Field(default="INR", description="Currency symbol or code")
    needs_clarification: bool = Field(description="True if flights are requested but origin or destination is missing")
    clarification_question: Optional[str] = Field(default=None, description="User-friendly question to ask the user")
    optimized_prompt: str = Field(description="Clean, fully articulated search prompt for the travel planner")

optimizer_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a travel search query optimizer.
Today's date is {current_date}.

Your tasks:
1. Correct typos (e.g. 'budyer' -> 'budget').
2. Always resolve dates to the current or upcoming year (never in the past!). If today is 2026, '15 october' means '2026-10-15'.
3. Always extract city names in friendly plain English (e.g. 'Mumbai', 'Goa'), NEVER IATA codes (no BOM, GOI).
4. If flights are requested or implied but the departure city is missing, set needs_clarification=True and generate a warm, friendly question asking which city they will be departing from.
5. Create a clean, comprehensive `optimized_prompt` summarizing all constraints for the search agent.
"""),
    ("human", "Conversation History:\n{history}\n\nLatest User Message: {message}")
])

optimizer_llm = ChatMistralAI(model="ministral-3b-latest", temperature=0)
optimizer_chain = optimizer_prompt | optimizer_llm.with_structured_output(ExtractedTravelIntent)

def optimize_user_query(message: str, history: str = "") -> ExtractedTravelIntent:
    current_date = datetime.now().strftime("%Y-%m-%d")
    return optimizer_chain.invoke({
        "current_date": current_date,
        "history": history,
        "message": message
    })
