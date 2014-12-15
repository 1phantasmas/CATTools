#!/usr/bin/env python
import os,sys,getopt

requestName = "test"
publishDataName = "caTuple"
datasets = []
inputFile =""
submit = False
try:
    opts, args = getopt.getopt(sys.argv[1:],"hsi:n:",["requestName","inputFile"])
except getopt.GetoptError:          
    print 'Usage : ./submitCrab3.py -n <requestName> -i <inputFile>'
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print 'Usage : ./submitCrab3.py -n <requestName> -i <inputFile>'
        sys.exit()
    elif opt in ("-n", "--requestName"):
        requestName = arg
    elif opt in ("-s"):
        submit = True
    elif opt in ("-i", "--inputFile"):
        inputFile = arg
        lines = open(inputFile)
        datasets = lines.readlines()

print opts
    
for dataset in datasets:
    isMC = True
    crabcommand ='crab submit -c crabConfigMC.py'

    ### MC or Data?
    datatype = dataset.strip().split("/")[-1]
    if datatype == "AOD" or datatype == "MINIAOD" :
        isMC = False
        crabcommand ='crab submit -c crabConfigRD.py'

    ### adjusting label for requestName
    dataset = dataset.strip()
    if isMC :
        label = dataset.split("/")[1]
    else :
        label = dataset.split("/")[1]+"_"+dataset.split("/")[2]

    sendjob = crabcommand + " Data.publishDataName='%s' General.requestName='%s_%s' Data.inputDataset='%s'"%(publishDataName,requestName,label,dataset)
    print sendjob
    if submit:
        print "submiting job"
        #os.system(sendjob)
