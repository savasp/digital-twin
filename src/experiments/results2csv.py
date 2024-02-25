import os
import glob
import csv
import xlsxwriter

models = [
    "llama2-7b",
    "llama2-13b",
    "gemma-2b",
    "gemma-7b",
    "mistral",
    "mixtral",
]

contexts = [
    "vector",
]

data_sources = [
    "webpages-linkedin",
    "linkedin",
    "webpages",
]

def main():    
    results_path = os.path.dirname(os.path.realpath(__file__)) + "/results/run-2024.02.24/"

    for model in models:
        for ds in data_sources:
            xl_workbook = xlsxwriter.Workbook(f"{results_path}{model}_{ds}.xlsx")
            worksheet = xl_workbook.add_worksheet()
            worksheet.write("A1", "Question")
            worksheet.write("B1", "Answer")
            worksheet.write("C1", "Latency")
            
            for i in range(1, 31):
                questions_file = open(results_path + f"{model}_{ds}_vector_{i}.txt", "r")
                question = questions_file.readline()
                latency = float(questions_file.readline())
                answer = "".join(questions_file.readlines())
            
                row = i + 1
                worksheet.write(f"A{row}", question)
                worksheet.write(f"B{row}", answer)
                worksheet.write(f"C{row}", latency)
            
            xl_workbook.close()
        
if __name__ == "__main__":
    main()
