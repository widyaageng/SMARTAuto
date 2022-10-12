#type: ignore
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from pathlib import Path
import os
import re
import configparser
from collections import OrderedDict
import pdb
##########################################


################################# UTILS #################################

def flatten(xs):
    result = []
    if isinstance(xs, (list, tuple)):
        for x in xs:
            result.extend(flatten(x))
    else:
        result.append(xs)
    return result


# webdriver setting
# TEMPLATE: http://rws01442418/SMART/ManageTestGroups?toolType=<commaseparatedtooltype>&toolSubType=<testedPN>}
# To Create Parameter based on ini file

DUTName = input("Enter DUT Name, case- and space-sensitive:\n")
DUTName = re.sub("\s+", "%20", DUTName)
DUTPartNumber = input("Enter DUT PartNumber, usually 9 digit in CWI:\n")
# flatten test
config = configparser.ConfigParser()
configFileName = input(
    "Enter .ini file that has been run after CreateTestGroups.py:\n")
config.read(configFileName)
smartweb = f"http://rws01442418/SMART/ManageTestGroups?toolType={DUTName}&toolSubType={DUTPartNumber}"
driverPath = os.path.join(str(Path.cwd()), 'msedgedriver.exe')
driver = webdriver.Edge(executable_path=driverPath)


# constant declarations and retrieval from ini file
unitsId = ['Degree C',
           'Counts',
           'Degrees',
           'Hertz',
           'milliAmps',
           'Numbers',
           'Voltage',
           'V/Gauss',
           'milliseconds',
           'seconds',
           'Percentage',
           'Amps',
           'MilliVolts',
           'Micro Farad',
           'K hertz',
           'Resistance',
           'Gravity',
           'RPM',
           'dB',
           'dBm',
           'Gs',
           'Micro Second',
           'bin',
           'mdB',
           'mDeg',
           'degree F']



testCaseRaw = [i for i in config['TESTGROUP']]
mainTest = [config['TESTGROUP'][i].split(",") for i in testCaseRaw]

for i, e in enumerate(mainTest):
    prefix = ''
    if (len(e) > 1):
        prefix = testCaseRaw[i] + "-"
    else:
        prefix = testCaseRaw[i]
    for k, j in enumerate(e):
        e[k] = prefix + j

mainTest = flatten(mainTest)

exceptionKeys = {'Group Number', 'Group Id'}
groupId = []
tempDict = {}

# Main param library
testParamDict = []
for i in mainTest:
    tempDict = OrderedDict(zip(config[i].keys(), config[i].values()))
    for j, key in enumerate(tempDict.keys()):
        groupId.append(tempDict['Group Id'])
        if key in exceptionKeys:
            pass
        else:
            tempArgs = tempDict[key].split(',')
            testParamDict.append(OrderedDict({
                'GroupId': tempDict['Group Id'],
                'TestGroupId': i,
                'Units': tempArgs[0],
                'Parameter': key,
                'Limit Type': tempArgs[1],
                'Parameter#': tempArgs[2],
                'PF Evaluated': tempArgs[3]
            }))
            
            """ To include ambient limits if any """
            if len(tempArgs)==6:
                testParamDict[-1]['AmbientLimit'] = [tempArgs[4], tempArgs[5]]
            
            """ To include hot limits if any """
            if len(tempArgs)==8:
                testParamDict[-1]['AmbientLimit'] = [tempArgs[4], tempArgs[5]]
                testParamDict[-1]['HotLimit'] = [tempArgs[6], tempArgs[7]]

            """ To include cold limits if any """
            if len(tempArgs)==10:
                testParamDict[-1]['AmbientLimit'] = [tempArgs[4], tempArgs[5]]
                testParamDict[-1]['HotLimit'] = [tempArgs[6], tempArgs[7]]
                testParamDict[-1]['ColdLimit'] = [tempArgs[8], tempArgs[9]]
            

groupId = list(set(groupId))
groupId.sort()

pdb.set_trace()


def xpath_testparam_listgen(groupIdarg):
    return [
        f"//a[contains(@href, 'ManageTestParameters/Index?groupId={groupIdarg}')]",
        f"//a[contains(@href, 'ManageTestParameters/Create?groupId={groupIdarg}')]"
    ]

xpath_testparam_list = [xpath_testparam_listgen(i) for i in groupId]
driver.get(smartweb)

"""Clicking test parameters on the same row as test group"""
def goToTestGroup(idx, testParamObj):
    elem = driver.find_element_by_xpath(f"//a[contains(@href, 'ManageTestParameters/Index?groupId={testParamObj[idx]['GroupId']}')]")
    if (elem.text == 'Test Parameters'):
        elem.click()
    else:
        raise Exception("It's not landed into test paramater!")

""" ENTRY: To create new param based on groupNumber index in groupId array"""
def createNewParam(idx, testParamObj):
    elem = driver.find_element_by_xpath(f"//a[contains(@href, 'ManageTestParameters/Create?groupId={testParamObj[idx]['GroupId']}')]")
    if (elem.text == 'Create New'):
        elem.click()
    else:
        raise Exception("It's not landed into create new test parameter!")

""" ENTRY: To edit existing param"""
def goEditParam(idx, testParamObj):
    elem = driver.find_element_by_xpath(f"//td[contains(text(), '{testParamObj[idx]['Parameter']}')]//parent::tr/td[8]/a")
    if (elem.tag_name == 'a' and elem.text == 'Edit'):
        elem.click()
    else:
        raise Exception("It's not landed into Edit button!")

""" To save edited param"""
def saveEditParam():
    elem = driver.find_element_by_xpath(f"//input[contains(@type, 'submit') and contains(@value, 'Save')]")
    elemAttritbuteValue = elem.get_attribute('value')
    if (elemAttritbuteValue == 'Save'):
        elem.click()
    else:
        raise Exception("It's not landed into \'Save\' submit type!")

"""############################ To Iterate thru testParamDict ############################"""
""" To select TestGroupId """
def selectTestGroupId(idx, testParamObj):
    elem = driver.find_element_by_xpath(f"//select[contains(@name, 'TestGroupId')]")
    if (elem.text.split("\n")[0] == testParamDict[0]['TestGroupId'].split("-")[-1]):
        selectElem = Select(elem)
        selectElem.select_by_visible_text(testParamObj[idx]['TestGroupId'].split("-")[-1])
    else:
        raise Exception("It's not landed into selectable test cases!")

""" To select Units """
def selectUnit(idx, testParamObj):
    elem = driver.find_element_by_xpath(f"//select[contains(@name, 'UnitsId')]")
    if (elem.text.split(" ")[0] == unitsId[0].split(" ")[0]):
        selectElem = Select(elem)
        selectElem.select_by_visible_text(testParamObj[idx]['Units'])
    else:
        raise Exception("It's not landed into Units selectable units!")

""" To enter Parameter Name """
def enterParameterName(idx, testParamObj):
    elem = driver.find_element_by_xpath(f"//input[contains(@name, 'ParameterName')]")
    if (elem.get_attribute('id') == 'ParameterName'):
        elem.clear()
        elem.send_keys(testParamObj[idx]['Parameter'])
    else:
        raise Exception("It's not landed into input field Parameter#!")

""" To select Limit Type """
def selectLimitType(idx, testParamObj):
    elem = driver.find_element_by_xpath(f"//select[contains(@name, 'LimitDataTypeId')]")
    if (elem.get_attribute('id') == 'LimitDataTypeId'):
        selectElem = Select(elem)
        selectElem.select_by_visible_text(testParamObj[idx]['Limit Type'])
    else:
        raise Exception("It's not landed into Parameter Limit Type selectable!")

""" To select Parameter Number """
def selectParameterNumber(idx, testParamObj):
    elem = driver.find_element_by_xpath(f"//input[contains(@name, 'ParameterNumber')]")
    if (elem.get_attribute('id') == 'ParameterNumber'):
        elem.clear()
        elem.send_keys(testParamObj[idx]['Parameter#'])
    else:
        raise Exception("It's not landed into field Parameter#!")

""" To select P/F evaluated """
def selectPFEvaluated(idx, testParamObj):
    elem = driver.find_element_by_xpath(f"//input[contains(@name, 'PassOrFailEvaluated')]")
    if (elem.get_attribute('id') == 'PassOrFailEvaluated'):
        if (str(elem.is_selected()) != testParamObj[idx]['PF Evaluated']):
            elem.click()
    else:
        raise Exception("It's not landed into field P/F Evaluated Parameter#!")

""" To submit form by clicking create button """
def createAndSubmitParam():
    elem = driver.find_element_by_xpath(f"//input[contains(@type, 'submit') and contains(@value, 'Create')]")
    elemAttritbuteValue = elem.get_attribute('value')
    if (elemAttritbuteValue == 'Create'):
        elem.click()
    else:
        raise Exception("It's not landed into \'Create\' submit type!")

""" To go back to List of Params """
def goBackToList():
    elem = driver.find_element_by_xpath(f"//a[contains(text(), 'Back to List')]")
    if (elem.text == 'Back to List'):
        elem.click()
    else:
        raise Exception("It's not landed into Back to List button!")

""" To go back to Test Groups"""
def goBackToTestGroups():
    elem = driver.find_element_by_xpath(f"//a[contains(text(), 'Back to Test Groups')]")
    if (elem.text == 'Back to Test Groups'):
        elem.click()
    else:
        raise Exception("It's not landed into Back to Test Groups button!")


def createNewParamRoutine(idx, testParamObj):
    goToTestGroup(idx, testParamObj)
    createNewParam(idx, testParamObj)
    selectTestGroupId(idx, testParamObj)
    selectUnit(idx, testParamObj)
    enterParameterName(idx, testParamObj)
    selectLimitType(idx, testParamObj)
    selectParameterNumber(idx, testParamObj)
    selectPFEvaluated(idx, testParamObj)
    createAndSubmitParam()
    goBackToTestGroups()

for i in range(len(testParamDict)):
    createNewParamRoutine(i, testParamDict)