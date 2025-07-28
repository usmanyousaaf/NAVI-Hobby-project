import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langgraph.graph import StateGraph, END
from typing import Dict, List, TypedDict

# Set OpenAI key
os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# Define the state schema
class ChatState(TypedDict):
    messages: List[Dict[str, str]]
    interests: List[str]
    dislikes: List[str]
    lifestyle: Dict[str, str]
    suggested_hobbies: List[str]
    phase: str
    user_id: str
    num_suggestions: int 

# Define hobby knowledge base
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

# System prompts
GREETING_PROMPT = """You are HobbyMentor, a friendly AI hobby coach. 
Greet the user warmly and ask about their interests. Keep it conversational and short.
Ask what kinds of things they enjoy doing in their free time.make the coversation engaging not just a list of questions or a quick suggestion."""

INTERESTS_PROMPT = """You are HobbyMentor. The user has shared their interests: {interests}
Ask follow-up questions about their interests to understand them better.
Then ask about things they dislike or want to avoid in hobbies.
Keep the conversation natural and engaging."""

DISLIKES_PROMPT = """You are HobbyMentor. 
User's interests: {interests}
User's dislikes: {dislikes}
Now ask about their lifestyle - how much time they have, their energy levels, 
and whether they prefer social or solo activities. Keep it conversational."""

LIFESTYLE_PROMPT = """You are HobbyMentor.
User's interests: {interests}
User's dislikes: {dislikes}  
User's lifestyle: {lifestyle}
Acknowledge their lifestyle preferences and transition to suggesting hobbies.
Say you'll start suggesting some perfect hobbies for them."""

SUGGESTION_PROMPT = """You are HobbyMentor. Based on the user's profile, suggest ONE specific hobby at a time.
User's interests: {interests}
User's dislikes: {dislikes}
User's lifestyle: {lifestyle}
Previously suggested: {suggested_hobbies}
→ DO NOT suggest any hobby from the 'Previously suggested' list.
Suggest ONE new hobby that fits their profile. Explain WHY it fits them specifically.
Ask if they'd like to know more about this hobby or want another suggestion.
Be encouraging and personal in your recommendations."""

# Extraction prompts
EXTRACT_INTERESTS_PROMPT = """Extract interests from this user message. Return only JSON.
User message: "{message}"
Return format: {{"interests": ["interest1", "interest2"]}}
If no interests mentioned, return {{"interests": []}}"""

EXTRACT_DISLIKES_PROMPT = """Extract dislikes/things to avoid from this user message. Return only JSON.
User message: "{message}"  
Return format: {{"dislikes": ["dislike1", "dislike2"]}}
If no dislikes mentioned, return {{"dislikes": []}}"""

EXTRACT_LIFESTYLE_PROMPT = """Extract lifestyle information from this user message. Return only JSON.
User message: "{message}"
Return format: {{"lifestyle": {{"energy": "high/medium/low", "time": "lots/some/little", "social": "social/solo/both"}}}}
If no lifestyle info mentioned, return {{"lifestyle": {{}}}}"""



def start_node(state: ChatState) -> ChatState:
    prompt = ChatPromptTemplate.from_template(GREETING_PROMPT)
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({})
    return {
        "messages": state["messages"] + [{"role": "assistant", "content": response}],
        "interests": state["interests"],
        "dislikes": state["dislikes"],
        "lifestyle": state["lifestyle"],
        "suggested_hobbies": state["suggested_hobbies"],
        "phase": "interests",
        "user_id": state["user_id"],
        "num_suggestions": state["num_suggestions"]
    }

def interests_node(state: ChatState) -> ChatState:
    user_message = state["messages"][-1]["content"] if state["messages"] and state["messages"][-1]["role"] == "user" else ""
    new_interests = []
    if user_message.strip():
        extract_prompt = ChatPromptTemplate.from_template(EXTRACT_INTERESTS_PROMPT)
        extract_chain = extract_prompt | llm | JsonOutputParser()
        try:
            extracted = extract_chain.invoke({"message": user_message})
            new_interests = extracted.get("interests", [])
        except Exception as e:
            print(f"Error extracting interests: {e}")

    # Merge and deduplicate
    updated_interests = list(set(state["interests"] + new_interests))

    # Generate response
    response_prompt = ChatPromptTemplate.from_template(INTERESTS_PROMPT)
    response_chain = response_prompt | llm | StrOutputParser()
    response = response_chain.invoke({"interests": updated_interests})

    return {
        "messages": state["messages"] + [{"role": "assistant", "content": response}],
        "interests": updated_interests,
        "dislikes": state["dislikes"],
        "lifestyle": state["lifestyle"],
        "suggested_hobbies": state["suggested_hobbies"],
        "phase": "dislikes",
        "user_id": state["user_id"],
        "num_suggestions": state["num_suggestions"]
    }

def dislikes_node(state: ChatState) -> ChatState:
    user_message = state["messages"][-1]["content"] if state["messages"] and state["messages"][-1]["role"] == "user" else ""
    new_dislikes = []
    if user_message.strip():
        extract_prompt = ChatPromptTemplate.from_template(EXTRACT_DISLIKES_PROMPT)
        extract_chain = extract_prompt | llm | JsonOutputParser()
        try:
            extracted = extract_chain.invoke({"message": user_message})
            new_dislikes = extracted.get("dislikes", [])
        except Exception as e:
            print(f"Error extracting dislikes: {e}")

    updated_dislikes = list(set(state["dislikes"] + new_dislikes))

    response_prompt = ChatPromptTemplate.from_template(DISLIKES_PROMPT)
    response_chain = response_prompt | llm | StrOutputParser()
    response = response_chain.invoke({
        "interests": state["interests"],
        "dislikes": updated_dislikes
    })

    return {
        "messages": state["messages"] + [{"role": "assistant", "content": response}],
        "interests": state["interests"],
        "dislikes": updated_dislikes,
        "lifestyle": state["lifestyle"],
        "suggested_hobbies": state["suggested_hobbies"],
        "phase": "lifestyle",
        "user_id": state["user_id"],
        "num_suggestions": state["num_suggestions"]
    }

def lifestyle_node(state: ChatState) -> ChatState:
    user_message = state["messages"][-1]["content"] if state["messages"] and state["messages"][-1]["role"] == "user" else ""
    new_lifestyle = {}
    if user_message.strip():
        extract_prompt = ChatPromptTemplate.from_template(EXTRACT_LIFESTYLE_PROMPT)
        extract_chain = extract_prompt | llm | JsonOutputParser()
        try:
            extracted = extract_chain.invoke({"message": user_message})
            new_lifestyle = extracted.get("lifestyle", {})
        except Exception as e:
            print(f"Error extracting lifestyle: {e}")

    merged_lifestyle = {**state["lifestyle"], **new_lifestyle}

    response_prompt = ChatPromptTemplate.from_template(LIFESTYLE_PROMPT)
    response_chain = response_prompt | llm | StrOutputParser()
    response = response_chain.invoke({
        "interests": state["interests"],
        "dislikes": state["dislikes"],
        "lifestyle": merged_lifestyle
    })

    return {
        "messages": state["messages"] + [{"role": "assistant", "content": response}],
        "interests": state["interests"],
        "dislikes": state["dislikes"],
        "lifestyle": merged_lifestyle,
        "suggested_hobbies": state["suggested_hobbies"],
        "phase": "suggesting",
        "user_id": state["user_id"],
        "num_suggestions": state["num_suggestions"]
    }

def suggestion_node(state: ChatState) -> ChatState:
    user_message = state["messages"][-1]["content"] if state["messages"] and state["messages"][-1]["role"] == "user" else ""

    response_prompt = ChatPromptTemplate.from_template(SUGGESTION_PROMPT)
    response_chain = response_prompt | llm | StrOutputParser()
    response = response_chain.invoke({
        "interests": state["interests"],
        "dislikes": state["dislikes"],
        "lifestyle": state["lifestyle"],
        "suggested_hobbies": state["suggested_hobbies"]
    })

    new_suggested_hobbies = state["suggested_hobbies"].copy()
    for category, hobbies in HOBBY_KNOWLEDGE_BASE.items():
        for hobby in hobbies:
            if hobby.lower() in response.lower() and hobby not in new_suggested_hobbies:
                new_suggested_hobbies.append(hobby)

    new_messages = state["messages"] + [{"role": "assistant", "content": response}]

    return {
        "messages": new_messages,
        "interests": state["interests"],
        "dislikes": state["dislikes"],
        "lifestyle": state["lifestyle"],
        "suggested_hobbies": new_suggested_hobbies,
        "phase": "suggesting",
        "user_id": state["user_id"],
        "num_suggestions": state["num_suggestions"] + 1  # Increment safely
    }

# --- Routing Logic ---
def route_conversation(state: ChatState) -> str:
    phase = state.get("phase", "start")
    num_suggestions = state.get("num_suggestions", 0)

    if phase == "start":
        return "interests"
    elif phase == "interests":
        return "dislikes"
    elif phase == "dislikes":
        return "lifestyle"
    elif phase == "lifestyle":
        return "suggesting"
    elif phase == "suggesting":
        if num_suggestions >= 3:
            return END
        return "suggesting"
    else:
        return END

# --- Build Graph ---
def create_chat_graph():
    workflow = StateGraph(ChatState)
    workflow.add_node("start", start_node)
    workflow.add_node("interests", interests_node)
    workflow.add_node("dislikes", dislikes_node)
    workflow.add_node("lifestyle", lifestyle_node)
    workflow.add_node("suggesting", suggestion_node)

    workflow.set_entry_point("start")
    workflow.add_conditional_edges("start", route_conversation)
    workflow.add_conditional_edges("interests", route_conversation)
    workflow.add_conditional_edges("dislikes", route_conversation)
    workflow.add_conditional_edges("lifestyle", route_conversation)
    workflow.add_conditional_edges("suggesting", route_conversation)

    return workflow.compile()

# --- Session Management ---
chat_graph = create_chat_graph()
sessions: Dict[str, ChatState] = {}

def get_or_create_session(user_id: str) -> ChatState:
    if user_id not in sessions:
        sessions[user_id] = {
            "messages": [],
            "interests": [],
            "dislikes": [],
            "lifestyle": {},
            "suggested_hobbies": [],
            "phase": "start",
            "user_id": user_id,
            "num_suggestions": 0
        }
    return sessions[user_id]

def process_message(user_id: str, message: str) -> str:
    try:
        state = get_or_create_session(user_id)
        if message.strip():
            state = {
                **state,
                "messages": state["messages"] + [{"role": "user", "content": message}]
            }

        # Invoke graph with higher recursion limit
        result = chat_graph.invoke(state, config={"recursion_limit": 50})
        sessions[user_id] = result

        assistant_msgs = [m for m in result["messages"] if m["role"] == "assistant"]
        return assistant_msgs[-1]["content"] if assistant_msgs else "Hello! How can I help you find a great hobby?"
    except Exception as e:
        print(f"Error processing message: {e}")
        return "I'm sorry, I encountered an error. Could you please try again?"

# --- FastAPI Endpoints ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id", "default")
        message = data.get("message", "")
        response = process_message(user_id, message)
        return JSONResponse({"type": "message", "text": response})
    except Exception as e:
        print(f"Error in chat_endpoint: {e}")
        return JSONResponse(
            {"type": "error", "text": "Sorry, I encountered an error. Please try again."},
            status_code=500
        )

@app.get("/api/reset/{user_id}")
async def reset_session(user_id: str):
    if user_id in sessions:
        del sessions[user_id]
    return JSONResponse({"status": "reset"})

@app.get("/api/status/{user_id}")
async def get_status(user_id: str):
    if user_id in sessions:
        session = sessions[user_id]
        return JSONResponse({
            "phase": session["phase"],
            "interests": session["interests"],
            "dislikes": session["dislikes"],
            "lifestyle": session["lifestyle"],
            "suggested_hobbies": session["suggested_hobbies"],
            "message_count": len(session["messages"])
        })
    return JSONResponse({"error": "Session not found"}, status_code=404)

@app.get("/health")
async def health_check():
    return JSONResponse({"status": "healthy"})

# Serve frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
