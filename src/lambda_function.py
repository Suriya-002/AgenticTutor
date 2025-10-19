import os
import json
from typing import TypedDict, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.aws import DynamoDbSaver
from langchain_openai import ChatOpenAI
import boto3

try:
    llm = ChatOpenAI(model="gpt-4", temperature=0.3)
except Exception as e:
    print(f"Could not initialize OpenAI client: {e}")
    llm = None

def generate_explanation(user_query: str) -> dict:
    print("---  EXPLAINING ---")
    if not llm: return {"explanation": "LLM not configured.", "context": ""}
    
    simulated_context = (
        "Beta measures a stock's volatility relative to the market. A Beta of 1 means it moves with the market. "
        "A Beta greater than 1 is more volatile, while a Beta less than 1 is less volatile. "
        "The CAPM formula uses Beta to calculate expected return."
    )
    system_prompt = "You are a Content Agent. Explain concepts clearly using ONLY the provided 'Context'."
    prompt = f"Context: {simulated_context}\n\nStudent asks: {user_query}"
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)], {"system_message": system_prompt})
        return {"explanation": response.content, "context": simulated_context}
    except Exception as e:
        print(f"Error in Content Agent: {e}")
        return {"explanation": "Error generating explanation.", "context": simulated_context}

def generate_question(explanation: str) -> dict:
    print("---  QUIZZING ---")
    if not llm: return {"question": "LLM not configured."}

    system_prompt = "You are a Quiz Agent. Create one short question based ONLY on the key concept in the provided 'Text'."
    prompt = f"Text: {explanation}"
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)], {"system_message": system_prompt})
        return {"question": response.content}
    except Exception as e:
        print(f"Error in Quiz Agent: {e}")
        return {"question": "Error generating question."}

def give_feedback(question: str, user_answer: str, context: str) -> dict:
    print("--- GIVING FEEDBACK ---")
    if not llm: return {"feedback_text": "LLM not configured."}

    system_prompt = (
        "You are a Feedback Agent. Analyze the student's answer based ONLY on the 'Context'. "
        "Return a single string of feedback. If correct, be encouraging. "
        "If incorrect, be gentle and explain why based on the context."
    )
    prompt = f"Context: {context}\nQuestion: {question}\nAnswer: {user_answer}"
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)], {"system_message": system_prompt})
        return {"feedback_text": response.content}
    except Exception as e:
        print(f"Error in Feedback Agent: {e}")
        return {"feedback_text": "Error evaluating answer."}


class TutorState(TypedDict):
    messages: List[BaseMessage]
    context: str
    question: str

def explain_node(state: TutorState):
    user_query = state["messages"][-1].content
    result = generate_explanation(user_query)
    ai_message = AIMessage(content=result["explanation"])
    return {"messages": [ai_message], "context": result["context"], "question": ""}

def quiz_node(state: TutorState):
    explanation = state["messages"][-1].content
    result = generate_question(explanation)
    ai_message = AIMessage(content=result["question"])
    return {"messages": [ai_message], "question": result["question"]}

def feedback_node(state: TutorState):
    question = state["question"]
    context = state["context"]
    user_answer = state["messages"][-1].content
    result = give_feedback(question, user_answer, context)
    ai_message = AIMessage(content=result["feedback_text"])
    return {"messages": [ai_message]}

graph_builder = StateGraph(TutorState)
graph_builder.add_node("explain", explain_node)
graph_builder.add_node("quiz", quiz_node)
graph_builder.add_node("feedback", feedback_node)

graph_builder.set_entry_point("explain")
graph_builder.add_edge("explain", "quiz")
graph_builder.add_edge("quiz", "feedback")
graph_builder.add_edge("feedback", END)

try:
    table_name = os.getenv("SESSIONS_TABLE_NAME")
    if not table_name:
        raise ValueError("SESSIONS_TABLE_NAME environment variable not set.")
    memory = DynamoDbSaver.from_table_name(table_name=table_name)
    graph = graph_builder.compile(checkpointer=memory)
    print("LangGraph compiled successfully with DynamoDB memory.")
except Exception as e:
    print(f" CRITICAL ERROR: Could not compile LangGraph: {e}")
    graph = None

def lambda_handler(event, context):
    if not graph:
        return {"statusCode": 500, "body": json.dumps({"error": "Graph is not compiled. Check Lambda logs."})}
    
    print(f"Received event: {json.dumps(event)}")
    
    try:
        user_id = event['requestContext']['authorizer']['claims']['sub']
        print(f"Authenticated user ID (sub): {user_id}")
    except (KeyError, TypeError):
        print("ERROR: Could not extract user_id ('sub') from authorizer claims.")
        return {"statusCode": 403, "body": json.dumps({"error": "Forbidden: User identifier not found."})}

    try:
        body = json.loads(event.get("body", "{}"))
        message_content = body.get("message")
        if not message_content: raise ValueError("Missing 'message' in request body.")
    except Exception as e:
        return {"statusCode": 400, "body": json.dumps({"error": f"Invalid request body: {e}"})}

    config = {"configurable": {"thread_id": user_id}}

    try:
        inputs = [HumanMessage(content=message_content)]
        final_state = None
        for chunk in graph.stream(inputs, config, stream_mode="values"):
            final_state = chunk
        
        ai_response = final_state["messages"][-1].content
        
        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"response": ai_response})
        }
    
    except Exception as e:
        print(f"ERROR: Graph execution failed for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return {"statusCode": 500, "body": json.dumps({"error": "An internal server error occurred."})}
