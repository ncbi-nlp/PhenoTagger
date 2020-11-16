import requests
import io
import sys
import re
import os
import time
from unidecode import unidecode
import bioc
from bioc import BioCCollection
import json

def PubTator_Converter(Inputfile,Outputfile,Originalfile):
	
	title_uni={}
	abstact_uni={}
	with open(Originalfile,'r', encoding='utf8') as file_Originalfile:
		title = ""
		abstract = ""
		for line in file_Originalfile:
			line = line.rstrip()
			p_title = re.compile('^([0-9]+)\|t\|(.*)$')
			p_abstract = re.compile('^([0-9]+)\|a\|(.*)$')
			if p_title.search(line):
				m = p_title.match(line)
				pmid = m.group(1)
				title = m.group(2)
				title_uni[pmid]=title
			elif p_abstract.search(line):
				m = p_abstract.match(line)
				pmid = m.group(1)
				abstract = m.group(2)
				abstact_uni[pmid]=abstract
					
	file_Originalfile.close()
	
	with open(Outputfile,'w', encoding='utf8') as file_Outputfile:
		with open(Inputfile,'r', encoding='utf8') as file_Inputfile:
			for line in file_Inputfile:
				line = line.rstrip()
				p_title = re.compile('^([0-9]+)\|t\|(.*)$')
				p_abstract = re.compile('^([0-9]+)\|a\|(.*)$')
				p_annotation = re.compile('^([0-9]+)	([0-9]+)	([0-9]+)	([^\t]+)	([^\t]+)(.*)')
				if p_title.search(line):  # title
					m = p_title.match(line)
					pmid = m.group(1)
					file_Outputfile.write(pmid+"|t|"+title_uni[pmid]+"\n")
				elif p_abstract.search(line):  # abstract
					m = p_abstract.match(line)
					pmid = m.group(1)
					file_Outputfile.write(pmid+"|a|"+abstact_uni[pmid]+"\n")
				elif p_annotation.search(line):  # annotation
					m = p_annotation.match(line)
					pmid = m.group(1)
					start = m.group(2)
					last = m.group(3)
					mention = m.group(4)
					type = m.group(5)
					id = m.group(6)
					tiabs=title_uni[pmid]+" "+abstact_uni[pmid]
					mention=tiabs[int(start):int(last)]
					file_Outputfile.write(pmid+"\t"+start+"\t"+last+"\t"+mention+"\t"+type+id+"\n")
				else:
					file_Outputfile.write(line+"\n")
			
		file_Outputfile.close()
	file_Inputfile.close()
	
def BioC_Converter(Inputfile,Outputfile,Originalfile):
	
	tiabs={}
	with open(Originalfile,'r', encoding='utf8') as file_Originalfile:
		collection = bioc.load(file_Originalfile)
		document_count=0
		for document in collection.documents:
			passage_count=0
			for passage in document.passages:
				if document_count not in tiabs:
					tiabs[document_count]={}
				tiabs[document_count][passage_count]=passage.text
				passage_count=passage_count+1
			document_count=document_count+1
	file_Originalfile.close()
	
	with open(Outputfile,'w', encoding='utf8') as file_Outputfile:
		with open(Inputfile,'r', encoding='utf8') as file_Inputfile:
			collection = bioc.load(file_Inputfile)
			document_count=0
			for document in collection.documents:
				passage_count=0
				for passage in document.passages:
					passage.text=tiabs[document_count][passage_count]
					for annotation in passage.annotations:
						start=annotation.locations[0].offset
						last=start+annotation.locations[0].length
						annotation.text=tiabs[document_count][passage_count][start:last]
					passage_count=passage_count+1
				document_count=document_count+1
			bioc.dump(collection, file_Outputfile, pretty_print=False)
		file_Inputfile.close()
	file_Outputfile.close()

def JSON_Converter(Inputfile,Outputfile,Originalfile):
	
	tiabs=""
	with open(Originalfile,'r', encoding='utf8') as file_Originalfile:
		collection = json.load(file_Originalfile)
		document_count=0
		tiabs=collection['text']
	file_Originalfile.close()
	
	with open(Outputfile,'w', encoding='utf8') as file_Outputfile:
		with open(Inputfile,'r', encoding='utf8') as file_Inputfile:
			collection = json.load(file_Inputfile)
			collection['text']=tiabs
			data=json.dumps(collection,  ensure_ascii=False)
			file_Outputfile.write(data)
		file_Inputfile.close()
	file_Outputfile.close()

def SubmitText(Inputfolder,Inputfile_SessionNumber,Outputfolder):
	
	#
	# load SessionNumbers
	#
	if not os.path.exists('tmp/'):
		os.makedirs('tmp/')
	with io.open(Inputfile_SessionNumber,'r',encoding="utf-8") as file_input:
		for line in file_input:
			pattern = re.compile('^([^\t]+)	(.+)$')
			if pattern.search(line):  # title
				m = pattern.match(line)
				SessionNumber = m.group(1)
				filename = m.group(2)
				
				if os.path.isfile(Outputfolder+"/"+filename):
					print(Outputfolder+"/"+filename+" - finished")
				else:
					#
					# retrieve result
					#
					r = requests.get("https://www.ncbi.nlm.nih.gov/research/pubtator-api/annotations/annotate/retrieve/" + SessionNumber)
					code = r.status_code
					if code == 200:
						response = r.text
						outputfile = open("tmp/"+filename, 'w')
						outputfile.write(response+"\n")
						outputfile.close()
						
						with open("tmp/"+filename, 'r', encoding='utf8') as file_input:
							format=""
							for line in file_input:
								pattern_json = re.compile('"sourcedb"')
								pattern_bioc = re.compile('.*<collection>.*')
								pattern_pubtator = re.compile('^([^\|]+)\|[^\|]+\|(.*)')
								if pattern_pubtator.search(line):
									format="PubTator"
									break
								elif pattern_bioc.search(line):
									format="BioC"
									break
								elif pattern_json.search(line):
									format="JSON"
									break
							if(format == "PubTator"):
								PubTator_Converter("tmp/"+filename,Outputfolder+"/"+filename,Inputfolder+"/"+filename)
								os.remove( "tmp/"+filename )
							elif(format == "BioC"):
								BioC_Converter("tmp/"+filename,Outputfolder+"/"+filename,Inputfolder+"/"+filename)
								os.remove( "tmp/"+filename )
							elif(format == "JSON"):
								JSON_Converter("tmp/"+filename,Outputfolder+"/"+filename,Inputfolder+"/"+filename)
								os.remove( "tmp/"+filename )
						
						print(SessionNumber+" : Result is retrieved.");
					else:
						print(SessionNumber+" : Result is not ready. please wait.");
					

if __name__ == "__main__":

	arg_count=0
	for arg in sys.argv:
		arg_count+=1
	if arg_count<2:
		print("\npython SubmitText.py [Inputfolder] [Inputfile_SessionNumber] [Outputfolder]\n")
		print("\t[Inputfolder]: Input folder")
		print("\t[Inputfile_SessionNumber]: a file with a list of SessionNumber")
		print("\t[Outputfolder]: Output folder")
		print("Eg., python SubmitText_retrieve.py input SessionNumber.txt output\n")
	else:
		Inputfolder = sys.argv[1]
		Inputfile_SessionNumber = sys.argv[2]
		Outputfolder = sys.argv[3]
		
		if not os.path.exists(sys.argv[3]):
			os.makedirs(sys.argv[3])
		SubmitText(Inputfolder,Inputfile_SessionNumber,Outputfolder)