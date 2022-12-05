from SpeakerPool.models import Account, StudyEntry
from SpeakerPool import app
import pandas as pd

accounts = Account.query.all()

study = input("What is the study number for which you would like to assemble the data? ")
study = "SpeakerPool/static/studies/" + study + "/data/"
enumFile = open(study + "enumeration.txt")
print("Generating dictionary from enum file")
lines = enumFile.readlines()
textDict = {}
for line in lines:
	line = line.split("\t")
	textDict[line[0]] = line[1]

print("Assembling for study", study) 
x = 0
nParticipants = len(accounts)
print(nParticipants, "participants found in database")
dataFile = open(study + "assembled.txt", "w")
n = 0
for account in range(nParticipants):
	x += 1
	try:
		logFile = open(str(study) + "logfiles/" + str(x) + ".txt", "r")
	except:
		print("Participant", x, "did not contribute any data to this study")
		continue
	
	contributions = logFile.readlines()
	nContributions = len(contributions)
	print("Participant", x, "contributed", nContributions, "recordings")
	if nContributions == 0:
		continue
	for contribution in contributions:
		contribution = contribution.strip("\n")
		split = contribution.split("\t")
		if split[3] != "SKIPPED":
			n += 1
			dataFile.write("wavs/" + split[3] + "|" + textDict[split[0]])
		
print("Assembled a list of", n, "files")
