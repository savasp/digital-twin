from typing import Any, Dict
from uuid import UUID
from langchain_core.documents import Document
from ..digital_twin.main_with_retrieval import *
import time
import os

llms = [
    "llama2:7b",
    "llama2:13b",
    "gemma:2b",
    "gemma:7b",
    "mistral",
    "mixtral",
]

pages = [
    "https://savas.me",
    "https://savas.me/about",
    "https://savas.me/cv",
    "https://savas.me/contact",
    "https://savas.me/publications",
]

dir_path = os.path.dirname(os.path.realpath(__file__))

linkedin_profile_folder = os.path.dirname(os.path.realpath(__file__)) + "../../../savas/"
json_docs = [
    linkedin_profile_folder + "Education.json",
    linkedin_profile_folder + "Email Addresses.json",
    linkedin_profile_folder + "Endorsement_Received_Info.json",
    linkedin_profile_folder + "Positions.json",
    linkedin_profile_folder + "Profile.json",
    linkedin_profile_folder + "Projects.json",
    linkedin_profile_folder + "Skills.json",    
]

questions_file = open(dir_path + "/questions.txt", "r")
questions = questions_file.readlines()

from langchain_core.messages import BaseMessage
class ChainInvokeHandler(BaseCallbackHandler):
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        formatted_prompts = "\n".join(prompts)
        #print(formatted_prompts)

def question_with_vector_context(chain: Runnable, question: str) -> str:
    response = chain.invoke({"input": question}, config={"callbacks": [ChainInvokeHandler()]})
    return response["answer"]
    
def question_with_context(chain: Runnable, question: str, docs: List[Document]) -> str:
    answer = chain.invoke({"input": question, "context": docs}, config={"callbacks": [ChainInvokeHandler()]})
    return answer

# Answer a question and record the result
def answer_questions(set_name: str, chain: Runnable, questions: List[str], docs: Optional[List[Document]] = None):
    print(set_name)
    print("-------------")
    
    if (docs is None):
        ask_question = lambda q: question_with_vector_context(chain, q)
    else:
        ask_question = lambda q: question_with_context(chain, q, docs)
        
    i = 1
    for question in questions:
        results_file = open(dir_path + f"/results/{set_name}_{i}.txt", "w")    
        i += 1
        print(question, end="...")
        start = time.perf_counter_ns()
        answer = ask_question(question)
        elapsed_ms = (time.perf_counter_ns() - start) / 1000000
        results_file.write(f"{question}{elapsed_ms}\n{answer}\n")
        print("done")

    print("=============")

def main():
    # Load all the docs
    webpages = ("webpages", load_web_pages(pages))
    linkedin_docs = ("linkedin", load_linkedin_json_docs(json_docs))
    all_docs = ("webpages-linkedin", webpages[1] + linkedin_docs[1])
 
    docs = [webpages, linkedin_docs, all_docs]
    
    # The prompt remains the same
    prompt = set_up_prompt()

    # For each of the LLM models we are using
    for model in llms:
        # For each set of docs
        for (ctx_title, ctx_docs) in docs:
            set_name_prefix =  f"/{model.replace(':', '-')}_{ctx_title}"
            
            # Set up the LLM
            llm = set_up_llm(model)

            # Build the chain using a vector representation of the context
            retrieval_chain = retrieval_based_chain(llm, prompt, ctx_docs)

            answer_questions(set_name_prefix + "_vector", retrieval_chain, questions)
            
            # Build the chain using the context as is
            #chain = direct_context_based_chain(llm, prompt, ctx_docs)
            
            # Answer the questions
            #answer_questions(set_name_prefix + "_direct", chain, questions, ctx_docs)
        
        
if __name__ == "__main__":
    main()
            
