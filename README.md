# Results of Pipeline

We store the results of our pipeline in the results folder. Due to file size, we only include the surface and sematnic similarity scores for the top 500 programs.

# Surface Level Similarity Score Section of Pipeline
This feature was written by Ansong Ni.

### Setup
- CORPUS_DIR: Location of the training dataset, this is what we will be searching through.
- TEST_FILE: File containing the canonical solutions for each question. This is what we will be searching for in the corpus.
- CHUNK_SIZE: Used for parralization.
- PROCESS_NUM: by default we use a pool of size 16. This can be changed depending on available hardware.

### Calling Surface Level Similarity Score Pipeline

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

### Calling Semantic Level Similarity Score Pipeline

```
python dolosmain.py
```