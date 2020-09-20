# PhenoTagger
***
This repo contains the source code and dataset for the PhenoTagger.

PhenoTagger is a hybrid method that combines dictionary and deep learning-based methods to recognize Human Phenotype Ontology (HPO) concepts in unstructured biomedical text. It is an ontology-driven method without requiring any manually labeled training data, as that is expensive and annotating a large-scale training dataset covering all classes of HPO concepts is highly challenging and unrealistic.

## Content
- [Dependency package](#package)
- [Data and model preparation](#preparation)
- [Instructions for tagging text with PhenoTagger](#tagging)
- [Instructions for training PhenoTagger](#training)

## Dependency package
<a name="package"></a>

PhenoTagger uses the following dependencies:

- [Python 3.7](https://www.python.org/)
- [TensorFlow 1.15.2](http://www.deeplearning.net/software/theano/)
- [Keras 2.3.1](http://www.numpy.org/)
- [nltk 3.5](www.nltk.org)
- [keras-bert 0.84.0](https://github.com/CyberZHG/keras-bert)


## Data and model preparation
<a name="preparation"></a>

1. To run this code, you need to first download BioBERT-Base v1.1 (https://github.com/dmis-lab/biobert), then put it into the /data/biobert_v11_pubmed/ folder. 
2. Two trained models (i.e., [BioBERT and CNN](https://ftp.ncbi.nlm.nih.gov/pub/lu/PhenoTagger/models.zip)) for HPO concept recognition are provided. You need to download it, and unzip to the PhenoTagger folder. If you want to use CNN model, you also should download the [pre-trined word embedding](https://ftp.ncbi.nlm.nih.gov/pub/lu/PhenoTagger/bio_embedding_intrinsic.zip) and unzip it into the /data/vocab/ folder. 
3. The corpora used in the experiments are provided in /data/corpus.zip

## Tagging free text with PhenoTagger
<a name="tagging"></a>

You can use our trained PhenoTagger to identify the HPO concepts from biomedical texts by the *PhenoTagger_tagging.py* file.


The file takes 2 parameters:

- --input, -i, help="the input file or file path"
- --output, -o, help="the output file"

For the input files, we can input a file or a path of the folder including the input text files.
The file format used is a simple tab-delimited format (Each document per line). The /example/ex1.txt and /example/ex2/ contain examples. 

Example:

```
python PhenoTagger_tagging.py -i ../example/ex1.txt -o ../example/ex1_pre.json
```

or 

```
python PhenoTagger_tagging.py -i ../example/ex2/ -o ../example/ex2_pre.json
```

We also provide some optional parameters for the different requirements of users in the *PhenoTagger_tagging.py* file.

```
para_set={
'tagger':'hybrid',    # three engines are provided.'dl' denotes only deep learning; 'dict' denotes only dictionary; 'hybrid' denote the hybrid method
'model_type':'cnn',   # two deep learning models are provided. cnn or biobert
'onlyLongest':False,  # False: return overlapping concepts; True: only return the longgest concepts in the overlapping concepts
'abbrRecog':False,    # False: don't identify abbreviation; True: identify abbreviations
'ML_Threshold':0.95,  # the Threshold of deep learning model
  }
```
After the program is finished, the JSON output file will be generated. The format of the JSON file is:

    {
      "text id": [
	    [
	      "concept start index",
	      "concept end index",
	      "concept text",
	      "HPO id",
	      "prediction score"
	    ],
        ....
      ]
    }

The /example/ex1_pre.json is an output example.


## Training PhenoTagger with a new ontology
<a name="training"></a>

### 1. Build the ontology dictionary using the *build_dict.py* file

The file takes 3 parameters:

- --input, -i, help="input the ontology .obo file"
- --output, -o, help="the output path of dictionary"
- --rootnode, -r, help="input the root node of the ontogyly"

Example:

```
python build_dict.py -i ../ontology/hp.obo -o ../dict/ -r HP:0000118
```

After the program is finished, 5 files will be generated in the outpath.

- id\_word\_map.json
- lable.vocab
- noabb\_lemma.dic
- obo.json
- word\_id\_map.json

### 2. Build the weakly-supervised training dataset using the *build_weak_corpus.py* file

The file takes 4 parameters:

- --dict, -d, help="the input path of the ontology dictionary"
- --fileneg, -f, help="the text file used to generate the negatives" (You can use our negative text ["mutation_disease.txt"](https://ftp.ncbi.nlm.nih.gov/pub/lu/PhenoTagger/mutation_disease.zip) )
- --negnum, -n, help="the number of negatives "
- --output, -o, help="the output path of the weakly-supervised training dataset"

Example:

```
python build_weak_corpus.py -d ../dict/ -f ../data/mutation_disease.txt -n 10000 -o ../data/weak_train_data/
```

After the program is finished, 3 files will be generated in the outpath.

- weak\_train.conll
- weak\_train\_pos.conll
- weak\_train\_neg.conll

### 3. Train PhenoTagger using the *PhenoTagger_training.py* file

The file takes 4 parameters:

- --trainfile, -t, help="the training file"
- --devfile, -d, help="the development set file. If don't provide the dev file, the training will be stopped by the specified EPOCH"
- --modeltype, -m, help="the deep learning model type (cnn or biobert?)"
- --output, -o, help="the model output file"

Example:

```
python PhenoTagger_training.py -t ../data/weak_train_data/weak_train.conll -d ../data/corpus/GSC/GSCplus_dev_gold.tsv -m biobert -o ../models/biobert_hpo.h5
```

After the program is finished, the trained model will be generated an the output.


## Disclaimer

This tool shows the results of research conducted in the Computational Biology Branch, NCBI. The information produced on this website is not intended for direct diagnostic use or medical decision-making without review and oversight by a clinical professional. Individuals should not change their health behavior solely on the basis of information produced on this website. NIH does not independently verify the validity or utility of the information produced by this tool. If you have questions about the information produced on this website, please see a health care professional. More information about NCBI's disclaimer policy is available.

***
