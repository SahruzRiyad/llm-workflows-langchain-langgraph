from langgraph.graph import Graph
from typing import TypedDict, List, Dict, Optional
import json
from pydantic import BaseModel
import sqlite3

import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# 1.State Definition
class EcommerceState(TypedDict):
    user_info: Dict
    user_input: str  # Required field
    message: Optional[str]
    intent: Optional[str]
    previous_step: Optional[str]  # Track conversation flow

# 2. Enhanced User Model with Pydantic
class User(BaseModel):
    user_id: Optional[int] = None
    name: str
    age: int 
    email: str 
    order_list: Optional[List[Dict]] = None
    interested_in: Optional[List[str]] = None

# 3. Database Functions (Fixed JSON Handling)
def connect_db():
    return sqlite3.connect("user.db")

def save_user(cursor, user: User):
    """Saves a User object to the database."""
    order_list_json = json.dumps(user.order_list) if user.order_list else None
    interested_in_json = json.dumps(user.interested_in) if user.interested_in else None

    if user.user_id is None: #insert new user
        cursor.execute('''
            INSERT INTO users (name, age, email, order_list, interested_in)
            VALUES (?, ?, ?, ?, ?)
        ''', (user.name, user.age, user.email, order_list_json, interested_in_json))
        user.user_id = cursor.lastrowid #get the generated id
    else: #update existing user
         cursor.execute('''
            UPDATE users SET name = ?, age = ?, email = ?, order_list = ?, interested_in = ?
            WHERE user_id = ?
        ''', (user.name, user.age, user.email, order_list_json, interested_in_json, user.user_id))

def add_users_sample():
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()

    # Creating table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            email TEXT UNIQUE,
            order_list TEXT,
            interested_in TEXT
        )
    ''')

    # Adding sample users
    user1 = User(name="Alice", age=30, email="alice@example.com", 
                order_list=[{"item": "book", "quantity": 1}], 
                interested_in=["reading", "coding"])
    user2 = User(name="Bob", age=25, email="bob@example.com", 
                interested_in=["sports"])
    user3 = User(name="Charlie", age=35, email="charlie@example.com")

    save_user(cursor, user1)
    save_user(cursor, user2)
    save_user(cursor, user3)

    conn.commit()
    conn.close()

# add_users_sample() 

def fetch_user_info(email: str) -> Dict:
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "user_id": user[0],
            "name": user[1],
            "age": user[2],
            "email": user[3],
            "order_list": json.loads(user[4]) if user[4] else [],
            "interested_in": json.loads(user[5]) if user[5] else []
        }
    return {
        "name": "Guest",
        "email": "",
        "order_list": [],
        "interested_in": []
    }

def greet_user(state: EcommerceState) -> EcommerceState:
    name = state["user_info"].get("name", "Guest")
    return {"message": f"Hello {name}! Welcome to our store. How can I assist you today?"}

def get_user_intent(state: EcommerceState) -> EcommerceState:
    # Ensure user_input exists, with empty string as fallback
    user_input = state.get("user_input", "")
    print(json.dumps(state))
    
    intent = "fallback"  # Default
    if "browse" in user_input.lower():
        intent = "browse"
    elif "order" in user_input.lower():
        intent = "order_status"
    elif "support" in user_input.lower():
        intent = "support"
    elif "recommend" in user_input.lower():
        intent = "recommendations"
    
    print(f"user-input: {user_input}, intent: {intent}")
    return {
        **state,  # Preserve all state
        "intent": intent,
        "previous_step": "detect_intent"
    }

def browse_product(state: EcommerceState) -> EcommerceState:
    categories = ["Electronics", "Fashion", "Home & Kitchen"]
    return {"message": f"Here are our categories: {', '.join(categories)}. What interests you?"}

def check_order_status(state: EcommerceState) -> EcommerceState:
    return {"message": "Please provide your order ID to check the status."}

def customer_support(state: EcommerceState) -> EcommerceState:
    return {"message": "What issue are you facing? I can assist with refunds, tracking, or general inquiries."}

def personalized_recommendations(state: EcommerceState) -> EcommerceState:
    interests = state["user_info"].get("interested_in", [])
    recommendations = {
        "reading": ["Book: 'Atomic Habits'", "E-reader"],
        "coding": ["Mechanical Keyboard", "Programming Course"],
        "sports": ["Running Shoes", "Yoga Mat"]
    }
    suggested = []
    for interest in interests:
        suggested.extend(recommendations.get(interest, []))
    return {"message": f"Based on your interests: {', '.join(interests)}, you might like: {', '.join(suggested[:3])}"}

def fallback(state: EcommerceState) -> EcommerceState:
    return {"message": "I'm not sure how to assist with that. Can you please rephrase?"}

# 5. Build the Corrected Graph
graph = Graph()

# Add nodes
graph.add_node("greet_user", greet_user)
graph.add_node("detect_intent", get_user_intent)
graph.add_node("browse", browse_product)
graph.add_node("order_status", check_order_status)
graph.add_node("support", customer_support)
graph.add_node("recommendations", personalized_recommendations)
graph.add_node("fallback", fallback)

# Set edges
graph.add_edge("greet_user", "detect_intent")

def route_intent(state: EcommerceState) -> str:
    return state.get("intent", "fallback")

graph.add_conditional_edges(
    "detect_intent",
    route_intent,
    {
        "browse": "browse",
        "order_status": "order_status",
        "support": "support",
        "recommendations": "recommendations",
        "fallback": "fallback"
    }
)

# Connect all endpoints back to detect_intent for continuous conversation
for node in ["browse", "order_status", "support", "recommendations", "fallback"]:
    graph.add_edge(node, "detect_intent")

graph.set_entry_point("greet_user")
workflow = graph.compile()

# 6. Test the Corrected Workflow

def run_chatbot(user_input: str, user_email: str = "alice@example.com") -> Dict:
    """Safe wrapper to run the chatbot"""
    user_info = fetch_user_info(user_email)
    
    initial_state: EcommerceState = {
        "user_info": user_info,
        "user_input": user_input,  # Guaranteed to exist
        "message": None,
        "intent": None,
        "previous_step": None
    }
    
    print(initial_state['user_input'])
    try:
        return workflow.invoke(initial_state)
    except Exception as e:
        return {
            "error": str(e),
            "message": "Sorry, something went wrong. Please try again."
        }

if __name__ == "__main__":
    test_inputs = [
        "I want to browse products",
        "Where is my order?",
        "I need customer support",
        "Can you recommend something?",
        "This is a random message"
    ]

    run_chatbot("Hi")
    for input_text in test_inputs:
        result = run_chatbot(input_text)
        print(f"Input: {input_text}")
        print(f"Response: {result.get('message')}\n")