from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from pathlib import Path
import os
import re

##########################################

# webdriver setting
# TEMPLATE: http://rws01442418/SMART/ManageTestGroups?toolType=<commaseparatedtooltype>&toolSubType=<testedPN>}
DUTName = input("Enter DUT Name, case- and space-sensitive:\n")
DUTName = re.sub("\s+", "%20", DUTName)
DUTPartNUmber = input("Enter DUT PartNumber, usually 9 digit in CWI:\n")
smartweb = f"http://rws01442418/SMART/ManageTestGroups?toolType={DUTName}&toolSubType={DUTPartNUmber}"
driverPath = os.path.join(str(Path.cwd()), 'msedgedriver.exe')
driver = webdriver.Edge(executable_path=driverPath)

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
groupId = [1832]  # input

testGroupId = [
    "CAN Diag Test",
    "20V 2A",
    "35V 1A",
    "48V 1A",
    "15V PRI",
    "15V Aux",
    "15V PRI Power Test",
    "SWRO Test",
    "Sensor Test",
    "MCC Test"]

paramsUnit = ["Voltage"]
paramsName = ["PS Voltage"]
paramsLimitType = ["Double"]
paramsNum = ["101"]
paramspfEvaluated = [True]
paramsDescription = ["Power taken from Main PS"]
paramsCreateOuterHTMLAttr = ["submit", "Create"]


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
if (elem.get_attribute('id')=='ParameterName'):
    elem.send_keys(paramsName[0])
else:
    raise Exception("It's not landed into input field Parameter#!")


elem = driver.find_element_by_xpath(xpath_testparam_list[0][5])
if (elem.get_attribute('id')=='LimitDataTypeId'):
    selectElem = Select(elem)
    selectElem.select_by_visible_text(paramsLimitType[0])
else:
    raise Exception("It's not landed into Parameter Limit Type selectable!")

elem = driver.find_element_by_xpath(xpath_testparam_list[0][6])
if (elem.get_attribute('id')=='ParameterNumber'):
    elem.clear()
    elem.send_keys(paramsNum[0])
else:
    raise Exception("It's not landed into field Parameter#!")

elem = driver.find_element_by_xpath(xpath_testparam_list[0][7])
if (elem.get_attribute('id')=='PassOrFailEvaluated'):
    if(paramspfEvaluated[0]):
        elem.click()
else:
    raise Exception("It's not landed into field P/F Evaluated Parameter#!")


elem = driver.find_element_by_xpath(xpath_testparam_list[0][8])
elemOuterHtml = elem.get_attribute('outerHTML')
elemAttritbueValue = re.findall(("\=\"[a-zA-Z]+\""))
if (elem.get_attribute('id')=='PassOrFailEvaluated'):
    if(all(a==b for a,b in zip(elemAttritbueValue, paramsCreateOuterHTMLAttr))):
        elem.click()
else:
    raise Exception("It's not landed into \'Create\' submit type!")