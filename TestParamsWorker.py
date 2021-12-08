from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from pathlib import Path
import os
import re
import configparser
from collections import OrderedDict
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
DUTName = input("Enter DUT Name, case- and space-sensitive:\n")
DUTName = re.sub("\s+", "%20", DUTName)
DUTPartNumber = input("Enter DUT PartNumber, usually 9 digit in CWI:\n")
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


# flatten test
config = configparser.ConfigParser()
configFileName = input(
    "Enter .ini file that has been run after CreateTestGroups.py:\n")
config.read(configFileName)

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
                'TestGroupId': i,
                'Units': tempArgs[0],
                'Parameter': key,
                'Limit Type': tempArgs[1],
                'Parameter#': tempArgs[2],
                'PF Evaluated': tempArgs[3]
            }))

groupId = list(set(groupId))
groupId.sort()
"""TODO:
1. Run driver, separated by TestGroupId to move between testgroups in testgroups page
2. Render the necessary parameters from library testParamDict to run all nethods below
3. Take note on separation between moving from testgrups page to test paramaters page
   Using: <a href="/SMART/ManageTestGroups?toolType={DUT Name  sub space with %20}&amp;toolSubType={DUTPartNUmber}">Back to Test Groups</a>
"""


def xpath_testparam_listgen(groupIdarg):
    return [
        f"//a[contains(@href, 'ManageTestParameters/Index?groupId={groupIdarg}')]",
        f"//a[contains(@href, 'ManageTestParameters/Create?groupId={groupIdarg}')]",
        f"//select[contains(@name, 'TestGroupId')]",
        f"//select[contains(@name, 'UnitsId')]",
        f"//input[contains(@name, 'ParameterName')]",
        f"//select[contains(@name, 'LimitDataTypeId')]",
        f"//input[contains(@name, 'ParameterNumber')]",
        f"//input[contains(@name, 'PassOrFailEvaluated')]",
        f"//input[contains(@type, 'submit') and contains(@value, 'Create')]"
    ]
"""Do I need to create wrapper on every time
it lands on the page with the name of parameter already exists.
Probably the easier method (brute):
1. Scan all the parameter that already exist in the page
2. Subtract the set of parameter that exist in page from list of paramater
   supposed to be written from blank state

"""

xpath_testparam_list = [xpath_testparam_listgen(i) for i in groupId]
driver.get(smartweb)

elem = driver.find_element_by_xpath(xpath_testparam_list[0][0])
if (elem.text == 'Test Parameters'):
    elem.click()
else:
    raise Exception("It's not landed into test paramater!")

elem = driver.find_element_by_xpath(xpath_testparam_list[0][1])
if (elem.text == 'Create New'):
    elem.click()
else:
    raise Exception("It's not landed into create new test parameter!")

elem = driver.find_element_by_xpath(xpath_testparam_list[0][2])
if (elem.text.split(" ")[0] == testGroupId[0].split(" ")[0]):
    selectElem = Select(elem)
    selectElem.select_by_visible_text(testGroupId[1])
else:
    raise Exception("It's not landed into selectable test cases!")

elem = driver.find_element_by_xpath(xpath_testparam_list[0][3])
if (elem.text.split(" ")[0] == unitsId[0].split(" ")[0]):
    selectElem = Select(elem)
    selectElem.select_by_visible_text(paramsUnit[0])
else:
    raise Exception("It's not landed into Units selectable units!")

elem = driver.find_element_by_xpath(xpath_testparam_list[0][4])
if (elem.get_attribute('id') == 'ParameterName'):
    elem.send_keys(paramsName[0])
else:
    raise Exception("It's not landed into input field Parameter#!")


elem = driver.find_element_by_xpath(xpath_testparam_list[0][5])
if (elem.get_attribute('id') == 'LimitDataTypeId'):
    selectElem = Select(elem)
    selectElem.select_by_visible_text(paramsLimitType[0])
else:
    raise Exception("It's not landed into Parameter Limit Type selectable!")

elem = driver.find_element_by_xpath(xpath_testparam_list[0][6])
if (elem.get_attribute('id') == 'ParameterNumber'):
    elem.clear()
    elem.send_keys(paramsNum[0])
else:
    raise Exception("It's not landed into field Parameter#!")

elem = driver.find_element_by_xpath(xpath_testparam_list[0][7])
if (elem.get_attribute('id') == 'PassOrFailEvaluated'):
    if(paramspfEvaluated[0]):
        elem.click()
else:
    raise Exception("It's not landed into field P/F Evaluated Parameter#!")


elem = driver.find_element_by_xpath(xpath_testparam_list[0][8])
elemOuterHtml = elem.get_attribute('outerHTML')
elemAttritbueValue = re.findall(("\=\"[a-zA-Z]+\""))
if (elem.get_attribute('id') == 'PassOrFailEvaluated'):
    if(all(a == b for a, b in zip(elemAttritbueValue, paramsCreateOuterHTMLAttr))):
        elem.click()
else:
    raise Exception("It's not landed into \'Create\' submit type!")
