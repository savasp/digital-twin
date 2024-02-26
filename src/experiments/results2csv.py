import os
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

def add_latency_chart(workbook):
    latency_worksheet = workbook.add_worksheet("_Latency")
    latency_chart = workbook.add_chart({"type": "column"})
    latency_chart.set_title({"name": "Latency"})
    latency_chart.set_x_axis({"name": "Question"})
    latency_chart.set_y_axis({"name": "Latency (ms)"})
    latency_chart.set_style(10)
    latency_worksheet.insert_chart("A1", latency_chart)

    for worksheet in workbook.worksheets():
        latency_chart.add_series({"values": f"='{worksheet.name}'!$D$2:$D$31", "name": f"{worksheet.name}"})
        
def add_avg_latency_chart(workbook):
    latency_worksheet = workbook.add_worksheet("_Avg latency")
    latency_chart = workbook.add_chart({"type": "column"})
    latency_chart.set_title({"name": "Avg latency"})
    latency_chart.set_x_axis({"name": "Configuration"})
    latency_chart.set_y_axis({"name": "Latency (ms)"})
    latency_chart.set_style(10)
    latency_worksheet.insert_chart("A1", latency_chart)

    worksheets = [w for w in workbook.worksheets() if not w.name.startswith("_")]
    series = list(set([w.name.split("_")[0] for w in worksheets]))
    categories_per_series = list(set([w.name.split("_")[1] for w in worksheets]))
    
    for i in range(0, len(series)):
        latency_worksheet.write(f"A{i + 1}", series[i])
        for j in range(0, len(categories_per_series)):
            row = i * len(categories_per_series) + j + 1
            latency_worksheet.write(f"B{row}", categories_per_series[j])
            latency_worksheet.write(f"C{row}", f"=AVERAGE('{series[i]}_{categories_per_series[j]}'!$D$2:$D$31)")

        from_row = i * len(categories_per_series) + 1
        to_row = from_row + len(categories_per_series) - 1
        latency_chart.add_series({
            "values": f"='{latency_worksheet.name}'!$C${from_row}:$C${to_row}",
            "name": series[i],
            "categories": f"='{latency_worksheet.name}'!$B${from_row}:$B${to_row}"})
    

def create_workbook():
    results_path = os.path.dirname(os.path.realpath(__file__)) + "/results/run-2024.02.24"

    xl_workbook = xlsxwriter.Workbook(f"{results_path}/results_code-generated.xlsx")
    format = xl_workbook.add_format({"align": "left", "valign": "vcenter", "text_wrap": True})
    
    for ds in data_sources:
        for model in models:
            worksheet = xl_workbook.add_worksheet()      
            worksheet.name = f"{ds}_{model}"
            worksheet.write("A1", "Question #")
            worksheet.write("B1", "Question")
            worksheet.write("C1", "Answer")
            worksheet.write("D1", "Latency")
            worksheet.write("E1", "Accuracy")
            worksheet.write("F1", "Quality")
            worksheet.write("G1", "1st Person Quality")
            
            for i in range(1, 31):
                questions_file = open(results_path + f"/{model}_{ds}_vector_{i}.txt", "r")
                question = questions_file.readline().removesuffix("\n")
                latency = float(questions_file.readline())
                answer = "".join(questions_file.readlines()).removesuffix("\n")
            
                row = i + 1
                worksheet.write(f"A{row}", i, format)
                worksheet.write(f"B{row}", question, format)
                worksheet.write(f"C{row}", answer, format)
                worksheet.write(f"D{row}", latency, format)
            
            worksheet.autofit()
            worksheet.set_column(0, 0, 3)
            worksheet.set_column(1, 1, 30)
            worksheet.set_column(2, 2, 100)
            worksheet.set_column(3, 3, 10)    
    return xl_workbook
    
def main():
    workbook = create_workbook()
    add_latency_chart(workbook)
    add_avg_latency_chart(workbook)

    workbook.close()
        
if __name__ == "__main__":
    main()
