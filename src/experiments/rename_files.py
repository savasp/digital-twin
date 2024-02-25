import os
import glob
        
def rename_files():
    results_path = os.path.dirname(os.path.realpath(__file__)) + "/results/run-2024.02.24/"
    files = glob.glob(results_path + "*webpages_linkedin*.txt")
    
    for f in files:
        new_name = f.replace("webpages_linkedin", "webpages-linkedin")
        os.rename(f, new_name)
    
if __name__ == "__main__":
    rename_files()
