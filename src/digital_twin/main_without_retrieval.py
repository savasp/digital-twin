# Savas' digital twin implementation

def setup_models():
    # Load the Llama model using the ChatOllama wrapper
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.3:70b", num_ctx=8192)
    
    return llm

def load_docs():
#    from langchain_community.document_loaders import JSONLoader
#    loader = JSONLoader("./linkedin-profile.json", jq_schema = ".", text_content=False)
#    docs = loader.load()
    from langchain_community.document_loaders import TextLoader
    loader = TextLoader("./linkedin-profile.txt")
    docs = loader.load()
    
    return docs

# Set up the graph
def setup_graph(llm, docs):
    from langgraph.graph import MessagesState, StateGraph
    from langchain_core.messages import SystemMessage

    # Generate the response
    def generate(state: MessagesState):
        """Generate answer."""

        # Format into prompt
        docs_content = "\n\n".join(doc.page_content for doc in docs)
        system_message_content = (
            "You are Savas Parastatidis' digital twin for question-answer tasks. "
            "Your name is Savas Parastatidis. "
            "You answer as if you are Savas Parastatidis. "
            "The following context contains information about you. "
            "Use this context to answer "
            "the question at the end. If you don't know the answer, say that you "
            "don't know. Keep your answer concise."
            "\n\n"
            f"{docs_content}"
        )
        conversation_messages = [
            message
            for message in state["messages"]
            if message.type in ("human", "system")
            or (message.type == "ai")
        ]
        prompt = [SystemMessage(system_message_content)] + conversation_messages

        # Run
        response = llm.invoke(prompt)
        return {"messages": [response]}

    graph_builder = StateGraph(MessagesState)
    
    from langgraph.graph import END

    graph_builder.add_node(generate)

    graph_builder.set_entry_point("generate")
    graph_builder.add_edge("generate", END)

    graph = graph_builder.compile()
    
    return graph

# Main function
def main():
    llm = setup_models()
    docs = load_docs()
    
    graph = setup_graph(llm, docs)
    
    questions = [
        "What is your name?",
        "When were you born?",
        "Where do you currently work?",
        "What is your work history?",
        "What did you do at Microsoft?",
        "What year did you start working on Cortana?",
        "Where did you study for your PhD degree?",
        "What year did you finish?",
        "What was the title of the thesis?",
        "Do you also have a masters degree?",
        "Where did you study for your bachelor's degree?",
        "Tell me about your skills.",
    ]
    
    for q in questions:
        for step in graph.stream(
            {"messages": [{"role": "user", "content": q}]},
            stream_mode="values",
            config={"configurable": {"thread_id": 42}}
        ):
            step["messages"][-1].pretty_print()    
    
# main entry point
if __name__=="__main__":
    main()