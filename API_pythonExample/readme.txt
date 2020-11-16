[Directory]
A. Summary of folders & files
B. Processing raw text online
C. Using the PubTator API efficiently

======================================================================================

A. [Summary of folders & files]
	
	Input & output:
		[input]
		[output]
		[tmp]
	Resource codes:
		SubmitText_request.py
		SubmitText_retrieve.py
	

B. [Processing raw text online] 
	
	To set up the environment:

		$ pip install -r requirements.txt

	The process consists of two primary steps 1) submitting requests and 2) retrieving results.
	
	1) Submitting requests : Three parameters are required, which include the name of the target folder containing files to process, the specific concept to retreive, and the output file to save the session numbers for later retrieval. Note that each session number represents the submission of one file.
	
		$ python SubmitText_request.py [Inputfolder] [Bioconcept:Phenotype] [Outputfile_SessionNumber]
        
		[Inputfolder]: a folder with files to submit
		[Bioconcept]: Phenotype
		[Outputfile_SessionNumber]: output file to save the session numbers

		Eg., python SubmitText_request.py input Phenotype SessionNumber.txt
	
	2) Retrieving results : Three parameters are required, which includes the original input folder, the filename containing session numbers, and the folder to store results. 
	
		$ python SubmitText_retrieve.py [Inputfolder] [Inputfile_SessionNumber] [Outputfolder]
        
		[Inputfolder]: Original Input folder
		[Inputfile_SessionNumber]: a file with a list of session numbers
		[Outputfolder]: Output folder

		Eg., python SubmitText_retrieve.py input SessionNumber.txt output

C. [Using the PubTator API efficiently]

	Each file in the input folder will be submitted for processing separately. After submission, each file may be queued for 10 to 20 minutes, depending on the computer cluster workload. Files then wait several additional minutes loading the trained models before processing can begin. System throughput is therefore significantly reduced if each file only contains a small amount of text. To improve efficiency, we suggest that each file contain roughly 100 abstracts or 5 full-text articles (100,000-200,000 characters). Note that some files may complete earlier than others; the estimated time to complete (ETC) is an estimate of the processing time for all files.
		
