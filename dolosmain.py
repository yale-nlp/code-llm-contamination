import os
import time
import json
import shutil
from multiprocessing import Pool


ZIP_DIR = "zipped"
PLAIN_DIR = "raw_files"
TEST_FILE = "human_eval_pile.jsonl"
PROCESS_NUM = 16

# itereate through folders in the zip folder
def call_dolos(folder_name):
    print("working on folder: ", folder_name)
    start = time.time()
    program_index = folder_name[len("problem_"):-len("_zipped")]
    program_results = []
    
    folder_path = os.path.join(ZIP_DIR, folder_name)
    
    for file in os.listdir(folder_path):
        # the order of the result is stored in the file's title
        index = int(file[len("high_score_number_"):-len("_zipped.zip")])
        
        file_path = os.path.join(folder_path, file)
        stream = os.popen(f"dolos run -f terminal --language python {file_path}")
        output = stream.read()
        output = output.split("\n")

        for line in output:
            if "Similarity score:" in line:
                score = float(line[len("Similarity score: "):])
                break
        
        program_results.append({"high_score_number": index, "score": score})

    sorted_program_results = sorted(program_results, key=lambda d: d["score"], reverse = True)

    end = time.time()
    run_time = end-start
    print("run time: ", run_time)

    result_dict = {
        "program_number": program_index,
        "sorted_program_results": sorted_program_results,
        "time": run_time
    }

    print("folder name: ", folder_name, "finished in ", run_time, " seconds with n = ", len(sorted_program_results), " results")

    # outputs the results to a file in the results folder
    output_path = "dolos_results"
    output_path = os.path.join(output_path, f"program_number_{program_index}")
    try:
        with open(output_path, "a+") as f:
            f.write(json.dumps(result_dict) + "\n")
    except FileNotFoundError:
        with open(output_path, "x") as f:
            f.write(json.dumps(result_dict) + "\n")


    return (program_index, sorted_program_results, run_time)

def zip_files():
    with open(TEST_FILE, "r") as f:
        results = [json.loads(s) for s in f.readlines()]

    # we begin by making sure the output folders for the individual programs and dolos zipped files exist
    try:
        os.mkdir(PLAIN_DIR)
    except:
        print(f"{PLAIN_DIR} already exists")
        
    try:
        os.mkdir(ZIP_DIR)
    except:
        print(f"{ZIP_DIR} already exists")
        
        
    # now we create the zipped files
    for i, result in enumerate(results):
        start = time.time()    
        gold_program = results[i]['test_str']   # since the gold program isn't stored in the file, we take it from the original dataset
        
        # make a folder to store the results in:
        start_index = i+1
        directory = f"Copyright_test_{start_index}"
        path = os.path.join(PLAIN_DIR, directory)
        try:
            os.mkdir(path)
        except:
            print("folder ", path, " already exists")

        # makes folder for zip files for Dolos
        directory = f"problem_{start_index}_zipped"    
        zip_path = os.path.join(ZIP_DIR, directory)
        try:
            os.mkdir(zip_path)
        except:
            print("folder ", zip_path, " already exists")
        

        for j, temp_result in enumerate(result['top_k']):
            # we only take the top 500 results
            if j >= 500:
                break

            # makes a folder for the gold program and subsring # num
            num_path = os.path.join(path, f"high_score_{j+1}")
            try:
                os.mkdir(num_path)
            except:
                print("folder ", num_path, " already exists")

            # writes the substring to the output path
            substring = temp_result["str"]
            output_path = os.path.join(num_path, f"high_score_{j+1}")
            try:
                with open(output_path, "w") as f:
                    f.write(substring)
            except:
                print("problem when writing to ", output_path, ".")

            # writes the gold program to the output path
            output_path = os.path.join(num_path, "gold_program")
            try:
                with open(output_path, "w") as f:
                    f.write(gold_program)
            except:
                print("problem writing gold program")        

            output_filename = os.path.join(zip_path, f"high_score_number_{j+1}_zipped")
            shutil.make_archive(output_filename, 'zip', num_path)
        
        end = time.time()
        print("time taken: ", end - start)

def main():

    # Dolos requires the input to be in a specific format, so we need to create zipped files for each question
    zip_files()

    folder_names = os.listdir(ZIP_DIR)

    with Pool(PROCESS_NUM) as p:
        results = p.map(call_dolos, folder_names)
        print(results)

if __name__ == "__main__":
    main()