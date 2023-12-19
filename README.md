# PhenoTagger v1.2
***
This repo contains the source code and dataset for the PhenoTagger.

PhenoTagger is a hybrid method that combines dictionary and deep learning-based methods to recognize Human Phenotype Ontology (HPO) concepts in unstructured biomedical text. It is an ontology-driven method without requiring any manually labeled training data, as that is expensive and annotating a large-scale training dataset covering all classes of HPO concepts is highly challenging and unrealistic. Please refer to our paper for more details:

- [Ling Luo, Shankai Yan, Po-Ting Lai, Daniel Veltri, Andrew Oler, Sandhya Xirasagar, Rajarshi Ghosh, Morgan Similuk, Peter N Robinson, Zhiyong Lu. PhenoTagger: A Hybrid Method for Phenotype Concept Recognition using Human Phenotype Ontology. Bioinformatics, Volume 37, Issue 13, 1 July 2021, Pages 1884–1890.](https://doi.org/10.1093/bioinformatics/btab019)


## Updates (2023-12-19):
- Use Transformers instead of kears-bert to load deep learning models.
- Use Tensorflow.keras instead of Keras.
- Add a [PubMedBERT](https://huggingface.co/microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext) model.  
- Re-train phenotype models using the newest version of HPO (hp/releases/2023-10-09)
- add negation and uncertainty detection function using [NegBio](https://github.com/ncbi-nlp/NegBio)



(2022-11-24)

-build a app demo for PhenoTagger

(2022-05-10):

-Fix some bugs to speed up the processing time.
-Add a Bioformer model (a light weight BERT in biomedical domain).
-Re-train phenotype models using the newest version of HPO (hp/releases/2022-04-14)

## Content
- [Dependency package](#package)
- [Data and model preparation](#preparation)
- [Instructions for tagging text with PhenoTagger](#tagging)
- [Instructions for training PhenoTagger](#training)
- [Performance on HPO GSC+](#performance)
- [Citing PhenoTagger](#citing)


## Dependency package
<a name="package"></a>
PhenoTagger has been tested using Python3.10 on CentOS and uses the following dependencies on a CPU and GPU:

- [TensorFlow 2.12.0](https://www.tensorflow.org/)
- [Transformers 4.30.1](https://huggingface.co/docs/transformers/index)
- [NLTK 3.8.1](www.nltk.org)


To install all dependencies automatically using the command:

```
$ pip install -r requirements.txt
```

## Data and model preparation
<a name="preparation"></a>

1. To run this code, you need to create a model folder named "models" in the PhenoTagger folder, then download the model files ( four trained models for HPO concept recognition are released, i.e., CNN, Bioformer, BioBERT, PubMedBERT) into the model folder.

	- First download original files of the pre-trained language models (PLMs): [Bioformer](https://huggingface.co/bioformers/bioformer-8L/), [BioBERT](https://huggingface.co/dmis-lab/biobert-base-cased-v1.2), [PubMedBERT](https://huggingface.co/microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext)
	- Then download the fine-tuned model files for HPO in [Here](https://huggingface.co/lingbionlp/PhenoTagger_v1.2/)

2. The corpora used in the experiments are provided in */data/corpus.zip*. Please unzip the file, if you need to use them.

## Tagging free text with PhenoTagger
<a name="tagging"></a>

You can use our trained PhenoTagger to identify the HPO concepts from biomedical texts by the *PhenoTagger_tagging.py* file.


The file requires 2 parameters:

- --input, -i, help="the folder with input files"
- --output, -o, help="output folder to save the tagged results"


The file format can be in BioC(xml) or PubTator(tab-delimited text file) (click [here](https://www.ncbi.nlm.nih.gov/research/bionlp/APIs/format/) to see our format descriptions). There are some examples in the */example/* folder. 

Example:

```
$ python PhenoTagger_tagging.py -i ../example/input/ -o ../example/output/
```


We also provide some optional parameters for the different requirements of users in the *PhenoTagger_tagging.py* file.

```
para_set={
'model_type':'bioformer',   # three deep learning models are provided: cnn, bioformer, biobert or pubmedbert
'onlyLongest':False,  # False: return overlapping concepts; True: only return the longgest concepts in the overlapping concepts
'abbrRecog':True,    # False: don't identify abbreviation; True: identify abbreviations
'negation': True, # True:negation detection
'ML_Threshold':0.95,  # the Threshold of deep learning model
}
```


## Training PhenoTagger with a new ontology
<a name="training"></a>

### 1. Build the ontology dictionary using the *Build_dict.py* file

The file requires 3 parameters:

- --input, -i, help="input the ontology .obo file"
- --output, -o, help="the output folder of dictionary"
- --rootnode, -r, help="input the root node of the ontogyly"

Example:

```
$ python Build_dict.py -i ../ontology/hp.obo -o ../dict/ -r HP:0000118
```

After the program is finished, 6 files will be generated in the output folder.

- id\_word\_map.json
- lable.vocab
- noabb\_lemma.dic
- obo.json
- word\_id\_map.json
- alt\_hpoid.json

### 2. Build the distantly-supervised training dataset using the *Build_distant_corpus.py* file

The file requires 4 parameters:

- --dict, -d, help="the input folder of the ontology dictionary"
- --fileneg, -f, help="the text file used to generate the negatives" (You can use our negative text ["mutation_disease.txt"](https://ftp.ncbi.nlm.nih.gov/pub/lu/PhenoTagger/mutation_disease.zip) )
- --negnum, -n, help="the number of negatives, we suggest that the number is the same with the positives."
- --output, -o, help="the output folder of the distantly-supervised training dataset"

Example:

```
$ python Build_distant_corpus.py -d ../dict/ -f ../data/mutation_disease.txt -n 10000 -o ../data/distant_train_data/
```

After the program is finished, 3 files will be generated in the outpath:

- distant\_train.conll       (distantly-supervised training data)
- distant\_train\_pos.conll  (distantly-supervised training positives)
- distant\_train\_neg.conll  (distantly-supervised training negatives)

### 3. Train PhenoTagger using the *PhenoTagger_training.py* file

The file requires 4 parameters:

- --trainfile, -t, help="the training file"
- --devfile, -d, help="the development set file. If don't provide the dev file, the training will be stopped by the specified EPOCH"
- --modeltype, -m, help="the deep learning model type (cnn, biobert, pubmedbert or bioformer?)"
- --output, -o, help="the output folder of the model"

Example:

```
$ python PhenoTagger_training.py -t ../data/distant_train_data/distant_train.conll -d ../data/corpus/GSC/GSCplus_dev_gold.tsv -m bioformer -o ../models/
```

After the program is finished, 2 files will be generated in the output folder:

- cnn.h5/biobert.h5                      (the trained model)
- cnn_dev_temp.tsv/biobert_dev_temp.tsv  (the prediction results of the development set, if you input a development set file)




## Citing PhenoTagger
<a name="citing"></a>

If you're using PhenoTagger, please cite:

*  Ling Luo, Shankai Yan, Po-Ting Lai, Daniel Veltri, Andrew Oler, Sandhya Xirasagar, Rajarshi Ghosh, Morgan Similuk, Peter N Robinson, Zhiyong Lu. [PhenoTagger: A Hybrid Method for Phenotype Concept Recognition using Human Phenotype Ontology](https://doi.org/10.1093/bioinformatics/btab019). Bioinformatics, Volume 37, Issue 13, 1 July 2021, Pages 1884–1890.




***
