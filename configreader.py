import configparser
import os
import json

curDirPath = os.path.abspath(os.path.dirname(__file__))
configFilePath = os.path.join(curDirPath, 'NGRPLC.ini')

config = configparser.ConfigParser()
config.optionxform = str
config.read(configFilePath)

testCase = [i for i in config['TESTGROUP'].keys()]
subTestCase = [i for i in config['TESTGROUP'].values()]
testCaseDict = dict(zip(testCase, subTestCase))

for key in testCaseDict.keys():
    if (len(testCaseDict[key]) > 0):
        testCaseDict[key] = testCaseDict[key].split(',')
    else:
        testCaseDict[key] = []
