from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.ui.select import Select
from pathlib import Path
import os

##########################################

# webdriver setting
# TEMPLATE: http://rws01442418/SMART/ManageTestGroups?toolType=<commaseparatedtooltype>&toolSubType=<testedPN>}

smartweb = "http://rws01442418/SMART/ManageTestGroups?toolType=NG%20Resistivity%20PLC&toolSubType=102973987"
driverPath = os.path.join(str(Path.cwd()), 'msedgedrive.exe')
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

groupId = 1832  # input
testGroupId = ["CAN Diag Test", "20V 2A"]
paramsUnit = ["Voltage"]
paramsName = ["PS Voltage"]
paramsLimitType = ["Double"]
paramsNum = ["101"]
paramspfEvaluated = [True]
paramsDescription = ["Power taken from Main PS"]

elem = driver.find_element_by_xpath(f"//a[contains(@href, 'ManageTestParameters/Index?groupId={groupId}')]")
if (elem.text == 'Test Parameters'):
    elem.click()
else:
    raise Exception("It's not landed into test paramater!")

elem = driver.find_element_by_xpath(f"//a[contains(@href, 'ManageTestParameters/Create?groupId={groupId}')]")
if (elem.text == 'Create New'):
    elem.click()
else:
    raise Exception("It's not landed into create new test parameter!")

elem = driver.find_element_by_xpath(f"//select[contains(@name, 'TestGroupId')]")
if (elem.text.split(" ")[0] == testGroupId[0].split(" ")[0]):
    selectElem = Select(elem)
    selectElem.select_by_visible_text(testGroupId[1])
else:
    raise Exception("It's not landed into selectable test cases!")

elem = driver.find_element_by_xpath(f"//select[contains(@name, 'UnitsId')]")
if (elem.text.split(" ")[0] == unitsId[0].split(" ")[0]):
    selectElem = Select(elem)
    selectElem.select_by_visible_text(paramsUnit[0])
else:
    raise Exception("It's not landed into Units selectable units!")

elem = driver.find_element_by_xpath(f"//input[contains(@name, 'ParameterName')]")
if (elem.get_attribute('id')=='ParameterName'):
    elem.send_keys(paramsName[0])
else:
    raise Exception("It's not landed into input field Parameter#!")


elem = driver.find_element_by_xpath(f"//select[contains(@name, 'LimitDataTypeId')]")
if (elem.get_attribute('id')=='LimitDataTypeId'):
    selectElem = Select(elem)
    selectElem.select_by_visible_text(paramsLimitType[0])
else:
    raise Exception("It's not landed into Parameter Limit Type selectable!")

elem = driver.find_element_by_xpath(f"//input[contains(@name, 'ParameterNumber')]")
if (elem.get_attribute('id')=='ParameterNumber'):
    elem.send_keys(paramsNum[0])
else:
    raise Exception("It's not landed into field Parameter#!")