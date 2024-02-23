from flask import Flask
from langchain_community.llms import Ollama

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

#if __name__ == '__main__':
#    app.run(debug = True, host = '0.0.0.0', port = 9123)

from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = Ollama(model = 'mistral')
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are world class technical documentation writer."),
    ("user", "{input}")
])

output_parser = StrOutputParser()

# Load a web page into the vector store
from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://savas.me/about")
docs = loader.load()

chain = prompt | llm | output_parser

#llm.invoke("how can langsmith help with testing?")
chain.invoke({"input", "how can langsmith help with testing?"})


