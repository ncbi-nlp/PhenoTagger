import requests
import io
import sys
import re
import os
import time
from unidecode import unidecode

def SubmitText_request(Inputfolder,Bioconcept,outputfile_SessionNumber):
	
	LengthArticles=0
	NumFiles=0
	with open(outputfile_SessionNumber, 'w', encoding='utf8') as outputfile:
		files = os.listdir(Inputfolder)
		for filename in files:
			# load text
			InputSTR=''
			with open(Inputfolder+"/"+filename,'r', encoding='utf8') as file_input:
				for line in file_input:
					line=unidecode(line)
					InputSTR = InputSTR + line
			file_input.close()
			
			if len(InputSTR)>LengthArticles:
				LengthArticles=len(InputSTR)
			NumFiles=NumFiles+1
			
			# submit request
			r = requests.post("https://www.ncbi.nlm.nih.gov/research/pubtator-api/annotations/annotate/submit/"+Bioconcept , data = InputSTR.encode('utf-8'))
			if r.status_code != 200 :
				print ("[Error]: HTTP code "+ str(r.status_code))
			else:
				SessionNumber = r.text
				print ("Thanks for your submission. The session number is : "+ SessionNumber + "\n")
				outputfile.write(SessionNumber+"\t"+filename+"\n")
	outputfile.close()
	
	# estimating process time
	Time4Waiting = NumFiles*200+250;
	Time4Preprocessing = 200;
	Time4Procesing = LengthArticles/800;
	EstimatedProcessTime = Time4Waiting + Time4Preprocessing + Time4Procesing;
	print ("Estimated time to complete : " + str(int(EstimatedProcessTime)) + " seconds");
	print ("Please use \"SubmitText_retrieve.py\" later to retrieve results.");

if __name__ == "__main__":

	arg_count=0
	for arg in sys.argv:
		arg_count+=1
	if arg_count<3:
		print("\npython SubmitText_request.py [Inputfolder] [Bioconcept:Phenotype] [outputfile_SessionNumber]\n")
		print("\t[Inputfolder]: a folder with files to submit")
		print("\t[Bioconcept]: Phenotype.")
		print("\t[outputfile_SessionNumber]: output file to save session numbers.")
		print("Eg., python SubmitText_request.py input Phenotype SessionNumber.txt\n")
	else:
		Inputfolder = sys.argv[1]
		Bioconcept = sys.argv[2]
		outputfile_SessionNumber = sys.argv[3]
		SubmitText_request(Inputfolder,Bioconcept,outputfile_SessionNumber)
