# Script to create textual descriptions from a JSON file containing
# facts about a person.

# Load the Llama model using the ChatOllama wrapper
from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.3:70b")

name = "Savas Parastatidis"
sections = {
    "education": f"These are facts about {name}'s education.",
    "profile": f"These are facts about {name}.",
    "jobs": f"These are facts about {name}'s work history.",
    "skills": f"This is a list of {name}'s skills.",
    "projects": f"These are facts about {name}'s projects.",
}

import json

with open('linkedin-profile.json', 'r') as file:
    profile = json.load(file)

for section in profile:
    prompt = (
        "The following is a JSON file with a set of facts.\n"
        f"{sections[section]}\n"
        "Generate a set of question and answer pairs for every fact. "
        "Make use of all the facts."
        "You can create multiple Q&A pairs for each fact."
        "Always refer to {name} by name."
        "Capture the dates when available. "
        "Only return the pairs. Do not number the pairs.\n\n"
        "Structure the response as: "
        "Question: <the question> "
        "Answer: <the answer> "
        "\n"
        f"{profile[section]}"
    )
    #response = llm.invoke(prompt)
    for event in llm.stream(prompt):
        print(event.content, end = "", flush = True)
        
    print("\n")
