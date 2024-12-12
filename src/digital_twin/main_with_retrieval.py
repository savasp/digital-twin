# Savas' digital twin implementation
# Based on the "Build a Retrieval Augmented Generation (RAG) App: Part 2"
# example at https://python.langchain.com/docs/tutorials/qa_chat_history.

# Set up the models
def setup_models():
    # Load the Llama model using the ChatOllama wrapper
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="llama3.3:70b")
    #llm = ChatOllama(model="llama3.2:3b")

    # Load the Llam embedding model using the Ollama Embeddings wrapper

    from langchain_ollama import OllamaEmbeddings

    embeddings = OllamaEmbeddings(model = "llama3.3:70b")
    #embeddings = OllamaEmbeddings(model = "llama3.2:3b")

    return llm, embeddings

# Set up the vector store
def setup_vector_store(embeddings):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
## ---- Load and chunk contents from Savas' online CV ----
#    from langchain_community.document_loaders import WebBaseLoader
#    import bs4
    
#    loader = WebBaseLoader(
#        web_paths=(
#            ["https://savas.me/cv", "https://savas.me/about"]
#        ),
#        bs_kwargs=dict(
#            parse_only=bs4.SoupStrainer(
#                class_=["entry-content"]
#            )
#        )
#    )

#    docs = loader.load()
#    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=100)
#    webpages_splits = text_splitter.split_documents(docs)

    # Index
 #   vector_store.add_documents(webpages_splits)

## ---- Load JSON version of the profile ----
#    from langchain_community.document_loaders import JSONLoader, DirectoryLoader

#    loader = DirectoryLoader("./linkedin-profile", glob='**/*.json', show_progress=False, loader_cls=JSONLoader, loader_kwargs = {'jq_schema':'.', 'text_content':False})
#    docs = loader.load()

## ---- Load text version of the profile ----
    from langchain_community.document_loaders import TextLoader
    loader = TextLoader("./linkedin-profile.txt")
    docs = loader.load()

## ---- Load Q&A version of the profile ----
#    from langchain_community.document_loaders import TextLoader
#    loader = TextLoader("./linkedin-profile-qa.txt")
#    docs = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    profile_splits = splitter.split_documents(docs)
    
    # Index
    #from langchain_community.vectorstores import InMemoryVectorStore
    #from langchain_community.vectorstores import Chroma
    #from langchain_community.vectorstores import FAISS
    from langchain_qdrant import QdrantVectorStore

    # vector_store = FAISS.from_documents(profile_splits, embeddings)
 
    vector_store = QdrantVectorStore.from_documents(
        profile_splits,
        embedding=embeddings,
        location=":memory:",
        collection_name="savas_digital_twin",
    )
    
    return vector_store

# Set up the graph
def setup_graph(llm, vector_store):
    from langgraph.prebuilt import tools_condition
    from langgraph.graph import MessagesState, StateGraph
    from langchain_core.messages import SystemMessage
    from langchain_core.tools import tool


    @tool(response_format="content_and_artifact")
    def retrieve(query: str):
        """Retrieve information related to a query."""
#        retriever = vector_store.as_retriever(
#            search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.6, "k": 10}
#        )
#        retrieved_docs = retriever.invoke(query)
#        retrieved_docs = retriever.similarity_search(query, k = 5)
        print(f"QUERY: {query} ===================")
        retrieved_docs = vector_store.similarity_search(query, k=4)
        serialized = "\n\n".join(
            (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs

    # Generate an AIMessage that may include a tool-call to be sent.
    def query_or_respond(state: MessagesState):
        """Generate tool call for retrieval or respond."""
        print(f"STATE: {state} ==================")
        llm_with_tools = llm.bind_tools([retrieve])
        response = llm_with_tools.invoke(state["messages"])
        print(f"RESPONSE: {response} ==================")

        # MessagesState appends messages to state instead of overwriting
        return {"messages": [response]}

    # Execute the retrieval.
    from langgraph.prebuilt import ToolNode
    tools = ToolNode([retrieve])
    
    # Generate the response
    def generate(state: MessagesState):
        """Generate answer."""
        # Get generated ToolMessages
        recent_tool_messages = []
        for message in reversed(state["messages"]):
            if message.type == "tool":
                recent_tool_messages.append(message)
            else:
                break
        tool_messages = recent_tool_messages[::-1]

        # Format into prompt
        docs_content = "\n\n".join(doc.content for doc in tool_messages)
        system_message_content = (
            "You are Savas Parastatidis' digital twin for question-answer tasks. "
            "You answer as if you are Savas Parastatidis, also known as 'assistant'. "
            "The following context contains information about Savas Parastatidis. "
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
            or (message.type == "ai" and not message.tool_calls)
        ]
        prompt = [SystemMessage(system_message_content)] + conversation_messages
        print(f"PROMPT: {prompt} =====================")

        # Run
        response = llm.invoke(prompt)
        return {"messages": [response]}

    graph_builder = StateGraph(MessagesState)
    
    from langgraph.graph import END

    graph_builder.add_node(query_or_respond)
    graph_builder.add_node(tools)
    graph_builder.add_node(generate)

    graph_builder.set_entry_point("query_or_respond")
    graph_builder.add_conditional_edges(
        "query_or_respond",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)

    from langgraph.checkpoint.memory import MemorySaver
    
    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)
    
    return graph

# Main function
def main():
    (llm, embeddings) = setup_models()
    vector_store = setup_vector_store(embeddings)
    
    graph = setup_graph(llm, vector_store)
    
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