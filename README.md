This pipeline was built to find similar programs within the training data of LLMs. It works in two stages, using the RapidFuzz library and Dolos software to find programs that are similar both on a surface level and semantically.  

# Results of Pipeline

We store the results of our pipeline in the results folder. Due to file size, we only include the surface and sematnic similarity scores for the top 500 programs.
The Levenshtein scores are ordered highest to lowest. Dolos scores are also ordered highest to lowest, with each program connected to their respective levenshtein scores with the key high_score_number. An example is that high_score_number": 1 corresponds to the program with the highest surface level similarity score.

# Surface Level Similarity Score Section of Pipeline
This feature was written by Ansong Ni. The RapidFuzz library is implemented to find programs that are similar to the gold program on a surface level. 

### Setup
- CORPUS_DIR: Location of the training dataset, this is what we will be searching through.
- TEST_FILE: File containing the canonical solutions for each question. This is what we will be searching for in the corpus.
- CHUNK_SIZE: Used for parralization.
- PROCESS_NUM: by default we use a pool of size 16. This can be changed depending on available hardware.

### Running Surface Level Similarity Score Pipeline

```
python main.py
```

# Semantic Level Similarity Score Section of Pipeline
The Dolos software requires each program to be zipped and stored seperatly within one folder. Once the programs are stored in the proper format, we can call the Dolos software on each folder. The zip_files() function works to create the folders properly formatted. After that the call_dolos() function works to call dolos on each of those folders.


### Setup
- ZIP_DIR: Folder to store zipped files.
- PLAIN_DIR: Location where programs are stored as plain text to be zipped.
- TEST_FILE: File containing the canonical solutions for each question. This is what we will be comparing each of the found programs to.
- PROCESS_NUM: by default we use a pool of size 16. This can be changed depending on available hardware.

### Running Semantic Level Similarity Score Pipeline

```
python dolosmain.py
```

# Citation

```
@misc{placeholder,
   author = {Martin Riddell and Ansong Ni and Arman Cohan},
   title = {Quantifying Contamination in Evaluating Code Generation Capabilities of Language Models},
   year={2024},
   publisher = {GitHub},
   journal = {GitHub repository},
   howpublished = {\url{https://github.com/yale-nlp/code-llm-contamination}}
}
```