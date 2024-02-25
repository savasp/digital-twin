# Functions to support the digital twin

from langchain_core.documents import Document
from typing import List, Optional
from langchain_core.runnables.config import RunnableConfig


####
def load_web_pages(page_uris: List[str]) -> List[Document]:
    """Loads web pages from a list of URIs.
    
    Args:
        page_uris (List[str]): A list of URIs for web pages.
        
    Returns:
        List[Document]: A list of Document objects, each containing the text content of a web page.
    """
    
    from langchain_community.document_loaders import WebBaseLoader
    
    loader = WebBaseLoader(page_uris)
    return loader.load()

####
def load_linkedin_json_docs(filenames: List[str]) -> List[Document]:
    """Loads a list of JSON files containing LinkedIn data.

    Args:
        filenames (List[str]): The list of filenames to load.

    Returns:
        List[Document]: A list of Document objects, each containing the data from a LinkedIn JSON file.
    """
    
    from langchain_community.document_loaders import JSONLoader

    docs = []    
    for file in filenames:
        loader = JSONLoader(file, jq_schema=".[]",text_content=False)
        docs += loader.load()
        
    return docs

####
from langchain_core.prompts import ChatPromptTemplate
def set_up_prompt() -> ChatPromptTemplate:
    """Sets up the LangChain prompt.

    Args:
        prompt_template (str): A string template for the LLM prompt.

    Returns:
        Prompt: The LangChain prompt.
    """

    system_template = """You are an AI that answers questions as if you were the human called Savas Parastatidis. You always respond in the first person. Be brief. Use one sentence answers when possible. It is ok to say "I don't know" if you don't know the answer. Only use information that you find in the provided context.

    <context>
    {context}
    </context>
    
    Question: {input}
    """
    
    prompt = ChatPromptTemplate.from_template(system_template)

    return prompt

####
from langchain_community.llms import Ollama
from langchain_core.callbacks.base import BaseCallbackHandler

def set_up_llm(model: str, handler: Optional[BaseCallbackHandler] = None) -> Ollama:
    """Sets up an LLM model.

    Args:
        model (str): The name of the LLM model to use (using Ollama names).
        handle (Optional[str]): The handler to use to get information from the chain.

    Returns:
        Ollama: The LLM representation.
    """

    if (handler is not None):
        prompt_handler = handler

        llm = Ollama(model=model, callbacks=[prompt_handler])
    else:
        llm = Ollama(model=model)
    
    return llm

####
from langchain_core.runnables import Runnable
def retrieval_based_chain(llm: Ollama, prompt: ChatPromptTemplate, docs: List[Document]) -> Runnable:
    """Creates a retrieval chain that uses retrieval from a vector database.

    Args:
        llm (Ollama)): The LLM model to use.
        prompt (ChatPromptTemplate): The LLM prompt to use.
        docs (List[Document]): The list of documents to add to the vector store.

    Returns:
        List[Document]: A list of documents, each containing the results of the retrieval chain.
    """
    
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    embeddings = OllamaEmbeddings(model = "mistral")
    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents(docs)
    vector = FAISS.from_documents(documents, embeddings)
    doc_chain = create_stuff_documents_chain(llm, prompt)

    # set up retrieval
    from langchain.chains import create_retrieval_chain

    retriever = vector.as_retriever()
    chain = create_retrieval_chain(retriever, doc_chain)

    return chain

####    
def direct_context_based_chain(llm: Ollama, prompt: ChatPromptTemplate, docs: List[Document]) -> Runnable:
    """Creates a simple chain.

    Args:
        llm (Ollama)): The LLM model to use.
        prompt (ChatPromptTemplate): The LLM prompt to use.
        docs (List[Document]): The list of documents to add to the vector store.

    Returns:
        List[Document]: A list of documents, each containing the results of the retrieval chain.
    """
    
    from langchain.chains.combine_documents import create_stuff_documents_chain

    context = ""
    for doc in docs:
        context += doc.page_content + "\n\n"

    chain = create_stuff_documents_chain(llm, prompt)
        
    return chain
