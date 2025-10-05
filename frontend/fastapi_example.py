"""
Example FastAPI backend for Stock AI Chat

This is a reference implementation showing how to structure your FastAPI backend
to work with the chat frontend.

To run this:
1. pip install fastapi uvicorn openai python-dotenv
2. Set your OPENAI_API_KEY in environment variables
3. uvicorn fastapi_example:app --reload --port 8000

The frontend is configured to call /api/chat endpoint.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure CORS to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat requests and return AI-generated stock recommendations
    """
    try:
        # Create a system prompt for stock recommendations
        system_prompt = """You are an AI stock advisor assistant. 
        Provide helpful, informative stock recommendations based on user queries.
        Always remind users that this is for informational purposes only and not financial advice.
        Keep responses concise and relevant to stock market queries."""
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or gpt-3.5-turbo for lower cost
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        
        ai_response = response.choices[0].message.content
        
        return ChatResponse(response=ai_response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
