import os
import json
import logging
import time

from multiprocessing import shared_memory, Pool
from io import StringIO
from thefuzz import fuzz
from tqdm import tqdm

CORPUS_DIR = "Github_Split"
CORPUS_FILES = [os.path.join(CORPUS_DIR, f"The_Pile_Github_Split_{i}.jsonl") for i in range(30)]

TEST_FILE = "HumanEval.jsonl"


# some parameters for parallelization
CHUNK_SIZE = 2_000_000  # by character
PROCESS_NUM = 16

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def find_for_program(test_str: str, shm_name: str = "human_eval_pile", threshold: int = 50, stride_percent: float = 0.05):
    # attach to the shared memory and decode it
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    chunk_str = existing_shm.buf[:].tobytes().decode("utf-8")

    # compute the scores
    scores = []
    stride = max(int(len(test_str) * stride_percent), 1)
    for i in range(0, len(chunk_str) - len(test_str), stride):
        score = fuzz.ratio(chunk_str[i:i+len(test_str)], test_str)
        scores.append(score)
    
    # we need to find the indices of the "peaks"
    peak_indices = []
    for i in range(len(scores)):
        if i == 0:
            if scores[i] > scores[i+1]:
                peak_indices.append((i, scores[i]))
            continue

        if i == len(scores) - 1:
            if scores[i] > scores[i-1]:
                peak_indices.append((i, scores[i]))
            continue

        if scores[i] >= scores[i-1] and scores[i] > scores[i+1]:
            peak_indices.append((i, scores[i]))
    
    # filter out the peaks that are below the threshold
    peak_indices = [peak for peak in peak_indices if peak[1] >= threshold]

    return peak_indices


def main():
    # load the test file
    logger.info("Reading test file...")
    with open(TEST_FILE, "r") as f:
        test_data = [json.loads(line) for line in f.readlines()]
    test_strs = [ex["canonical_solution"] for ex in test_data]

    # load the corpus files
    logger.info("Reading training corpus...")
    corpus_data = []
    for corpus_file in tqdm(CORPUS_FILES[:1]):  # FIXME: debug
        with open(corpus_file, "r") as f:
            corpus_data.extend([json.loads(line) for line in f.readlines()])
    
    # create the chunks first
    chunk_strs = []
    i = 0
    while True:
        str_builder = StringIO()
        while i < len(corpus_data) and str_builder.tell() < CHUNK_SIZE:
            str_builder.write(corpus_data[i]["text"])
            i += 1

        chunk_strs.append(str_builder.getvalue())        
        if i == len(corpus_data):
            break
    logger.info(f"Created {len(chunk_strs)} chunks")

    # sequential for corpus data and parallel for test program
    for chunk_str in tqdm(chunk_strs[:1]):  # FIXME: debug
        start = time.perf_counter()

        # create the shared memory and load data into it
        chunk_str_bytes = chunk_str.encode("utf-8")
        shm = shared_memory.SharedMemory(name="human_eval_pile", create=True, size=len(chunk_str_bytes))
        shm.buf[:len(chunk_str_bytes)] = chunk_str_bytes

        stop_1 = time.perf_counter()
        logger.debug(f"Created shared memory in {(stop_1 - start) * 1000} ms, starting parallel processes...")

        # create the processes, parallize for different test programs
        test_idx_strs = sorted(enumerate(test_strs), key=lambda x: len(x[1]), reverse=True)
        test_indices, test_strs = zip(*test_idx_strs)

        with Pool(PROCESS_NUM) as pool:
            results = pool.map(find_for_program, test_strs)
        
        # results = []
        # intervals = []
        # for test_str in tqdm(test_strs):
        #     stop_3 = time.perf_counter()
        #     results.append(find_for_program(test_str))
        #     stop_4 = time.perf_counter()
        #     intervals.append(stop_4 - stop_3)
        
        # print(f"Intervals: {sorted(intervals, reverse=True)}")
        
        shm.close()
        shm.unlink()
        
        stop_2 = time.perf_counter()
        logger.debug(f"Finished parallel processes in {stop_2 - stop_1} seconds")

if __name__ == "__main__":
    main()