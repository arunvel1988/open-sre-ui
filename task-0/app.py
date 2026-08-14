from flask import Flask, render_template, request, jsonify
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict

app = Flask(__name__)

# -----------------------------
# Ollama / Qwen3
# -----------------------------

llm = ChatOllama(
    model="qwen3:1.7b",
    base_url="http://localhost:11434",
    temperature=0,
)


# -----------------------------
# LangGraph state
# -----------------------------

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def agent(state: AgentState):

    response = llm.invoke(state["messages"])

    return {
        "messages": [response]
    }


# -----------------------------
# Build graph
# -----------------------------

graph = StateGraph(AgentState)

graph.add_node("agent", agent)

graph.add_edge(START, "agent")
graph.add_edge("agent", END)

agent_graph = graph.compile()


# -----------------------------
# Conversation memory
# -----------------------------

conversation = []


# -----------------------------
# Routes
# -----------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    global conversation

    data = request.get_json()

    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "error": "Message is empty"
        }), 400

    conversation.append(
        HumanMessage(content=message)
    )

    result = agent_graph.invoke({
        "messages": conversation
    })

    conversation = result["messages"]

    response = conversation[-1].content

    return jsonify({
        "response": response
    })


@app.route("/clear", methods=["POST"])
def clear():

    global conversation

    conversation = []

    return jsonify({
        "status": "cleared"
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )
