from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from pathlib import Path
import os
import re
import configparser
from collections import OrderedDict
import time
##########################################

DUTName = input("Enter UUT Type, case- and space-sensitive:\n")
UUTSubType = input(
    "Enter UUT Subtype according to smart system master database, case- and space-sensitive:\n")
TestLimitVersions = input("Test Limit Version (integer only):\n")

smartweb = f"http://rws01442418/SMART/ManageTestLimits"
driverPath = os.path.join(str(Path.cwd()), 'msedgedriver.exe')
driver = webdriver.Edge(executable_path=driverPath)
time.sleep(2)
driver.get(smartweb)


""" Navigate and pull the limit of UUT """
def selectUUTLimitTable(DUTName, UUTSubType, TestLimitVersions):
    elem = driver.find_element_by_xpath(f"//select[contains(@name, 'toolType')]")
    if DUTName in elem.text.split("\n"):
        selectElem = Select(elem)
        selectElem.select_by_visible_text(DUTName)
    else:
        raise Exception("UUT Type is not valid/mismatch with any database DUT!")
    
    time.sleep(3)
    elem = driver.find_element_by_xpath(f"//select[contains(@name, 'toolSubType')]")
    if UUTSubType in elem.text.split("\n"):
        selectElem = Select(elem)
        selectElem.select_by_visible_text(UUTSubType)
    else:
        raise Exception("UUT Subtype Name is not valid/mismatch with any database DUT!")
    
    time.sleep(3)
    elem = driver.find_element_by_xpath(f"//select[contains(@name, 'toolLimitVersion')]")
    if TestLimitVersions in elem.text.split("\n"):
        selectElem = Select(elem)
        selectElem.select_by_visible_text(TestLimitVersions)
    else:
        raise Exception("UUT TestLimitVersions is not valid/mismatch with any database DUT!")
    
    time.sleep(3)
    elem = driver.find_element_by_xpath(f"//input[contains(@type, 'submit') and contains(@value, 'Filter')]")
    if (elem.get_attribute('id') == 'filterButton'):
        elem.click()
    else:
        raise Exception("It's not landed into Filter button!")
