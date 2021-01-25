# PhenoTagger
***
This repo contains the source code and dataset for the PhenoTagger.

PhenoTagger is a hybrid method that combines dictionary and deep learning-based methods to recognize Human Phenotype Ontology (HPO) concepts in unstructured biomedical text. It is an ontology-driven method without requiring any manually labeled training data, as that is expensive and annotating a large-scale training dataset covering all classes of HPO concepts is highly challenging and unrealistic. Please refer to our paper for more details:

- [Ling Luo, Shankai Yan, Po-Ting Lai, Daniel Veltri, Andrew Oler, Sandhya Xirasagar, Rajarshi Ghosh, Morgan Similuk, Peter N Robinson, Zhiyong Lu. PhenoTagger: A Hybrid Method for Phenotype Concept Recognition using Human Phenotype Ontology. Bioinformatics, 2021, btab019.](https://doi.org/10.1093/bioinformatics/btab019)

## Content
- [Dependency package](#package)
- [Data and model preparation](#preparation)
- [Instructions for tagging text with PhenoTagger](#tagging)
- [Instructions for training PhenoTagger](#training)
- [Web API for PhenoTagger](#api)
- [Performance on HPO GSC+](#performance)
- [Citing PhenoTagger](#citing)
- [Acknowledgments](#ac)

## Dependency package
<a name="package"></a>
PhenoTagger have been tested using Python3.7 on CentOS and uses the following dependencies on a CPU and GPU:

TF2:
- [TensorFlow 2.3.0](https://www.tensorflow.org/)
- [Keras 2.4.3](http://www.numpy.org/)
- [nltk 3.5](www.nltk.org)
- [keras-bert 0.86.0](https://github.com/CyberZHG/keras-bert)

or TF1:
- [TensorFlow 1.15.2](http://www.deeplearning.net/software/theano/)
- [Keras 2.3.1](http://www.numpy.org/)
- [nltk 3.5](www.nltk.org)
- [keras-bert 0.84.0](https://github.com/CyberZHG/keras-bert)

To install all dependencies automatically using the command:

```
$ pip install -r requirements.txt
```

## Data and model preparation
<a name="preparation"></a>

1. To run this code, you need to first download [the model file](https://ftp.ncbi.nlm.nih.gov/pub/lu/PhenoTagger/models.zip) ( it includes some trained models, i.e., BioBERT-Base v1.1, pre-trained word embedding, two trained models for HPO concept recognition), then unzip and put the model folder into the Phenotagger folder.
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
'model_type':'biobert',   # two deep learning models are provided. cnn or biobert
'onlyLongest':False,  # False: return overlapping concepts; True: only return the longgest concepts in the overlapping concepts
'abbrRecog':False,    # False: don't identify abbreviation; True: identify abbreviations
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

After the program is finished, 5 files will be generated in the output folder.

- id\_word\_map.json
- lable.vocab
- noabb\_lemma.dic
- obo.json
- word\_id\_map.json

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
- --modeltype, -m, help="the deep learning model type (cnn or biobert?)"
- --output, -o, help="the output folder of the model"

Example:

```
$ python PhenoTagger_training.py -t ../data/distant_train_data/distant_train.conll -d ../data/corpus/GSC/GSCplus_dev_gold.tsv -m biobert -o ../models/
```

After the program is finished, 2 files will be generated in the output folder:

- cnn.h5/biobert.h5                      (the trained model)
- cnn_dev_temp.tsv/biobert_dev_temp.tsv  (the prediction results of the development set, if you input a development set file)


## Web API
<a name="api"></a>
We also provide Web API for PhenoTagger for ease of use. Due to the limitation of computing resources, the API is run on a CPU. If you have GPUs, we suggest you download the source code and run PhenoTagger on own server.

You can use it to process raw text in the same way as [Pubtotar API](https://www.ncbi.nlm.nih.gov/research/pubtator/api.html). You need to set \[Bioconcept\] parameter to "Phenotype". The code samples in python are found in *API_pythonExample* folder. 

The process consists of two primary steps 1) submitting requests and 2) retrieving results.
	
### 1. Submitting requests

```
$ python SubmitText_request.py [Inputfolder] [Bioconcept:Phenotype] [Outputfile_SessionNumber]
```

Three parameters are required:
        
- \[Inputfolder\]: a folder with files to submit
- \[Bioconcept\]: Phenotype
- \[Outputfile_SessionNumber\]: output file to save the session numbers

Example:

```
$ python SubmitText_request.py input Phenotype SessionNumber.txt
```
	
###	2. Retrieving results

```
$ python SubmitText_retrieve.py [Inputfolder] [Inputfile_SessionNumber] [outputfolder]
```

Three parameters are required:

- \[Inputfolder\]: original input folder	
- \[Inputfile_SessionNumber\]: a file with a list of session numbers
- \[Outputfolder\]: Output folder

Example:

```
$ python SubmitText_retrieve.py input SessionNumber.txt output
```

Note that each file in the input folder will be submitted for processing separately. After submission, each file may be queued for 10 to 20 minutes, depending on the computer cluster workload.

## Performance on HPO GSC+
<a name="performance"></a>

The following Table shows the results of PhenoTagger with the CNN and BioBERT models on the GSC+ test set. And the training/test time on one NVIDIA Tesla V100 GPU is provided. You can choose the appropriate model according to your needs.

| Method | Training/Test time | Men-P | Men-R | Men-F1 | Doc-P | Doc-R | Doc-F1 |
| ----------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| PhenoTagger (CNN) | 2h56m/106s | 0.772 | 0.706 | 0.738 | 0.735 | 0.706 | 0.720 |
| PhenoTagger (BioBERT) | 15h42m/152s | 0.789 | 0.722 | 0.754 | 0.774 | 0.740 | 0.757 |

Here, *h*, *m*, *s* denotes hour, minute and second, respectively. 


## Citing PhenoTagger
<a name="citing"></a>

If you're using PhenoTagger, please cite:

*  Ling Luo, Shankai Yan, Po-Ting Lai, Daniel Veltri, Andrew Oler, Sandhya Xirasagar, Rajarshi Ghosh, Morgan Similuk, Peter N Robinson, Zhiyong Lu. [PhenoTagger: A Hybrid Method for Phenotype Concept Recognition using Human Phenotype Ontology](https://doi.org/10.1093/bioinformatics/btab019). Bioinformatics, 2021, btab019.


## Acknowledgments 
<a name="ac"></a>

This research is supported by the Intramural Research Programs of the National Institutes of Health, National Library of Medicine.
Thanks to Dr. Chih-Hsuan Wei for his help with Web APIs.


## Disclaimer

This tool shows the results of research conducted in the Computational Biology Branch, NCBI. The information produced on this website is not intended for direct diagnostic use or medical decision-making without review and oversight by a clinical professional. Individuals should not change their health behavior solely on the basis of information produced on this website. NIH does not independently verify the validity or utility of the information produced by this tool. If you have questions about the information produced on this website, please see a health care professional. More information about NCBI's disclaimer policy is available.

***
