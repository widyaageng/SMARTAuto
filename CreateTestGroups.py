from selenium.webdriver import Edge
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import os
import re
import configparser
import json
from collections import OrderedDict
import math
import pdb

currentDirPath = os.path.abspath(os.path.dirname(__file__))
inifileName = input("Please Enter config file name (include .ini extension)\n")
testVIFilename = input("What's the VI filename? must be the same name as labview lvlib (ex: Lithostar PLC Board):\n")

if re.match("[a-zA-Z0-9]+\.ini", inifileName) is None:
    exit("Extension is not valid!")

configFilePath = os.path.join(currentDirPath, inifileName)

config = configparser.ConfigParser()
config.optionxform = str
config.read(configFilePath)
testCase = [i for i in config['TESTGROUP'].keys()]
subTestCase = [i for i in config['TESTGROUP'].values()]
testCaseDict = OrderedDict(zip(testCase, subTestCase))
paramsGroupNumber = []
groupIndexPointer = 0
testCaseCounter = 0

for key in testCaseDict.keys():
    if (len(testCaseDict[key]) > 0):
        testCaseDict[key] = testCaseDict[key].split(',')
    else:
        testCaseDict[key] = []

#### should be in for loop ####

def exitDriver():
    driver.quit()
    exit("Forced quit Error!")

def createTestGroup(grpIdxPtr, tstCsCount):
    for i in testCase:
        grpIdxPtr  = 100*math.floor(grpIdxPtr/100) + 100
        tstCsCount += 1
        try:
            elem = driver.find_element_by_xpath(f"//td[contains(text(), '{grpIdxPtr}')]")
            elem = elem.find_element_by_xpath("./..")
            if re.match(i, elem.text) is not None:
                if (len(testCaseDict[i]) > 0):
                    for tst in range(len(testCaseDict[i])):
                        grpIdxPtr += 1
                        tstCsCount += 1
                        try:
                            elem = driver.find_element_by_xpath(f"//td[contains(text(), '{grpIdxPtr}')]")
                            elem = elem.find_element_by_xpath("./..")
                            if re.match(testCaseDict[i][tst], elem.text) is not None:
                                continue
                            else:
                                exitDriver()
                        except:
                            elem = driver.find_element_by_xpath(f"//a[contains(text(), 'Create New')]")
                            elem.click()
                            elem = driver.find_element_by_xpath(f"//input[contains(@id, 'GroupName')]")
                            elem.send_keys(testCaseDict[i][tst])
                            elem = driver.find_element_by_xpath(f"//input[contains(@id, 'TestGroupNumber')]")
                            elem.send_keys(grpIdxPtr)
                            elem = driver.find_element_by_xpath(f"//input[contains(@type, 'submit')]")
                            elem.click()
            else:
                exitDriver()
            continue
        except:
            elem = driver.find_element_by_xpath(f"//a[contains(text(), 'Create New')]")
            elem.click()
            elem = driver.find_element_by_xpath(f"//input[contains(@id, 'GroupName')]")
            elem.send_keys(i)
            elem = driver.find_element_by_xpath(f"//input[contains(@id, 'TestGroupNumber')]")
            elem.send_keys(grpIdxPtr)
            elem = driver.find_element_by_xpath(f"//input[contains(@type, 'submit')]")
            elem.click()
            if (len(testCaseDict[i]) > 0):
                for tst in range(len(testCaseDict[i])):
                    grpIdxPtr += 1
                    tstCsCount += 1
                    try:
                        elem = driver.find_element_by_xpath(f"//td[contains(text(), '{grpIdxPtr}')]")
                        elem = elem.find_element_by_xpath("./..")
                        if re.match(testCaseDict[i][tst], elem.text) is not None:
                            continue
                        else:
                            exitDriver()
                    except:
                        elem = driver.find_element_by_xpath(f"//a[contains(text(), 'Create New')]")
                        elem.click()
                        elem = driver.find_element_by_xpath(f"//input[contains(@id, 'GroupName')]")
                        elem.send_keys(testCaseDict[i][tst])
                        elem = driver.find_element_by_xpath(f"//input[contains(@id, 'TestGroupNumber')]")
                        elem.send_keys(grpIdxPtr)
                        elem = driver.find_element_by_xpath(f"//input[contains(@type, 'submit')]")
                        elem.click()
    
    return grpIdxPtr, tstCsCount


def getTestGroupNumber():
    groupIndex = [i for i in range(testCaseCounter)]
    paramsGroupId  = [f"[{groupIndex[i]}].GroupId" for i in groupIndex]

    for i in paramsGroupId:
        elem = driver.find_element_by_xpath(f"//input[contains(@name, '{i}')]")
        paramsGroupNumber.append(elem.get_property("value"))

    ## write new groupId to ini file
    
    paramIdx = 0
    for i,e in enumerate(testCase):
        config[e]['Group Id'] = paramsGroupNumber[paramIdx]
        paramIdx += 1
        if (len(testCaseDict[e]) > 0):
            for j in testCaseDict[e]:
                config[e + "-" + j]['Group Id'] = paramsGroupNumber[paramIdx]
                paramIdx += 1


    with open('newExportConfigure.ini', 'w') as newConfigFile:
        config.write(newConfigFile)


DUTName = input("Enter DUT Name, case- and space -sensitive:\n")
DUTPartNUmber = input("Enter DUT PartNumber, usually 9 digit in CWI:\n")
webaddress = f"http://rws01442418/SMART/ManageTestGroups"

driver = Edge(executable_path=os.path.join(currentDirPath, "msedgedriver.exe"))
driver.get(webaddress)

elem = driver.find_element_by_xpath(f"//select[contains(@name, 'toolType')]")
select = Select(elem)
select.select_by_visible_text(testVIFilename)

elem = driver.find_element_by_xpath(f"//input[contains(@value, 'Filter')]")
elem.click()
groupIndexPointer, testCaseCounter = createTestGroup(groupIndexPointer, testCaseCounter)
getTestGroupNumber()
driver.quit()
exit


