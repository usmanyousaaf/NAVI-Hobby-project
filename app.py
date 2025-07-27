import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from typing import Dict, List, Optional
import json
import re
import openai

import os
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# Define system prompt
SYSTEM_PROMPT = """
You are HobbyMentor, an AI hobby coach and conversational partner.

# Goals
- Help the user discover new hobbies and activities that fit their unique personality, interests, dislikes, and lifestyle.
- Never give all suggestions at once. Focus on a slow, natural conversation where you introduce ideas step by step.
- Think like a psychologist and a mentor: build rapport, explore emotions and motivations, and inspire curiosity.
- Use the user's past messages to inform your suggestions and keep the conversation flowing naturally.
- Avoid generic lists or quick answers. Treat each suggestion as a personal recommendation based on their unique context.
- Always ask for their thoughts and feelings about each suggestion before moving on to the next one.
- Always speak less and listen more. Your goal is to understand them deeply before suggesting anything.
- Answer in short, to-the-point, human-like sentences. Avoid long sentences.

# Conversation Style
- Warm, encouraging, curious. Act like a friend who really wants to understand them.
- Use short back-and-forth turns. Ask clarifying questions before suggesting anything.
- When suggesting hobbies:
  * Suggest ONE idea at a time.
  * Explain WHY you think it fits them.
  * Ask them if they like the idea or want another suggestion.
- After they react, you can give another suggestion.
- Avoid dumping lists of hobbies or summarizing everything in one go.
- If they seem unsure or shy, motivate them gently with benefits and fun facts about the hobby.

# Information Gathering Steps
- Step 1: Ask about things they enjoy and what relaxes them.
- Step 2: Ask what they dislike or what drains them.
- Step 3: Ask about their lifestyle (energy level, available time, social preferences).
- Step 4: Once you have enough information, suggest hobbies slowly, in a conversational, human way.

# Rules
- Never output generic lists like "You could try A, B, C, D".
- Never skip directly to final answers.
- Use memory from past conversation.
- Stay curious and make the chat long and smooth.
"""

# Define knowledge base
HOBBY_KNOWLEDGE_BASE = {
    "music": ["playing an instrument", "singing", "music production", "joining a choir"],
    "outdoors": ["hiking", "camping", "bird watching", "gardening", "rock climbing"],
    "creative": ["painting", "writing", "photography", "knitting", "pottery", "drawing"],
    "social": ["board game nights", "book clubs", "volunteering", "dance classes"],
    "solo": ["reading", "puzzle solving", "journaling", "meditation", "collecting"],
    "active": ["yoga", "cycling", "swimming", "martial arts", "running"],
    "tech": ["coding", "3D printing", "electronics", "video editing"],
    "crafts": ["woodworking", "jewelry making", "sewing", "origami"]
}

class HobbyMentor:
    def __init__(self):
        self.conversation_prompt = ChatPromptTemplate.from_template(
            SYSTEM_PROMPT + """
            
            Current conversation phase: {phase}
            User's interests: {interests}
            User's dislikes: {dislikes}
            User's lifestyle: {lifestyle}
            Previously suggested hobbies: {suggested_hobbies}
            
            Conversation history:
            {conversation_history}
            
            User's latest message: "{user_message}"
            
            Respond naturally according to the current phase and conversation context.
            """
        )
        
        self.extraction_prompt = ChatPromptTemplate.from_template(
            """
            Extract information from the user's response. Return ONLY valid JSON.
            
            Current phase: {phase}
            User message: "{user_message}"
            
            Based on the phase, extract:
            - interests: If asking about interests, return {{"interests": ["interest1", "interest2"]}}
            - dislikes: If asking about dislikes, return {{"dislikes": ["dislike1", "dislike2"]}}  
            - lifestyle: If asking about lifestyle, return {{"lifestyle": {{"energy": "high/medium/low", "time": "lots/some/little", "social": "social/solo/both"}}}}
            - intent: If in suggestion phase, return {{"intent": "wants_more/satisfied/asking_question"}}
            
            If no relevant info, return {{}}.
            """
        )
        
        self.conversation_chain = self.conversation_prompt | llm | StrOutputParser()
        self.extraction_chain = self.extraction_prompt | llm | JsonOutputParser()

class UserSession:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.phase = "greeting"  # greeting -> interests -> dislikes -> lifestyle -> suggesting
        self.interests = []
        self.dislikes = []
        self.lifestyle = {}
        self.suggested_hobbies = []
        self.conversation_history = []
        self.message_count = 0

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
        self.message_count += 1

    def get_conversation_string(self) -> str:
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history[-6:]])  # Last 6 messages

    def advance_phase(self):
        phase_order = ["greeting", "interests", "dislikes", "lifestyle", "suggesting"]
        current_index = phase_order.index(self.phase)
        if current_index < len(phase_order) - 1:
            self.phase = phase_order[current_index + 1]

# Global session storage
sessions: Dict[str, UserSession] = {}
mentor = HobbyMentor()

def get_session(user_id: str) -> UserSession:
    if user_id not in sessions:
        sessions[user_id] = UserSession(user_id)
    return sessions[user_id]

def generate_response(session: UserSession, user_message: str = "") -> str:
    try:
        # Handle greeting phase
        if session.phase == "greeting":
            session.advance_phase()
            response = "Hi! I'm HobbyMentor, and I'd love to help you discover some amazing new hobbies. Let's start by getting to know you - what kinds of things do you enjoy doing in your free time?"
            session.add_message("assistant", response)
            return response

        # Add user message to history
        if user_message:
            session.add_message("user", user_message)

        # Extract information based on current phase
        extracted_info = {}
        if user_message:
            try:
                extracted_info = mentor.extraction_chain.invoke({
                    "phase": session.phase,
                    "user_message": user_message
                })
            except:
                extracted_info = {}

        # Update session with extracted info
        if "interests" in extracted_info:
            session.interests.extend(extracted_info["interests"])
        if "dislikes" in extracted_info:
            session.dislikes.extend(extracted_info["dislikes"]) 
        if "lifestyle" in extracted_info:
            session.lifestyle.update(extracted_info["lifestyle"])

        # Generate conversational response
        response = mentor.conversation_chain.invoke({
            "phase": session.phase,
            "interests": session.interests,
            "dislikes": session.dislikes,
            "lifestyle": session.lifestyle,
            "suggested_hobbies": session.suggested_hobbies,
            "conversation_history": session.get_conversation_string(),
            "user_message": user_message
        })

        # Advance phase based on context
        if session.phase == "interests" and session.interests:
            session.advance_phase()
        elif session.phase == "dislikes" and session.dislikes:
            session.advance_phase()
        elif session.phase == "lifestyle" and session.lifestyle:
            session.advance_phase()

        # Track suggested hobbies
        if session.phase == "suggesting":
            # Simple hobby extraction from response
            for category, hobbies in HOBBY_KNOWLEDGE_BASE.items():
                for hobby in hobbies:
                    if hobby.lower() in response.lower() and hobby not in session.suggested_hobbies:
                        session.suggested_hobbies.append(hobby)

        session.add_message("assistant", response)
        return response

    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm having trouble processing that. Could you tell me a bit about what you like to do for fun?"

# FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"], 
    allow_headers=["*"]
)

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id", "default")
        message = data.get("message", "")
        
        session = get_session(user_id)
        response = generate_response(session, message)
        
        return JSONResponse({
            "type": "message",
            "text": response
        })
        
    except Exception as e:
        print(f"Error in chat_endpoint: {e}")
        return JSONResponse({
            "type": "error",
            "text": "Sorry, I encountered an error. Please try again."
        }, status_code=500)

@app.get("/api/reset/{user_id}")
async def reset_session(user_id: str):
    if user_id in sessions:
        del sessions[user_id]
    return JSONResponse({"status": "reset"})

@app.get("/api/status/{user_id}")
async def get_status(user_id: str):
    session = get_session(user_id)
    return JSONResponse({
        "phase": session.phase,
        "interests": session.interests,
        "dislikes": session.dislikes,
        "lifestyle": session.lifestyle,
        "suggested_hobbies": session.suggested_hobbies,
        "message_count": session.message_count
    })

# Serve frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)