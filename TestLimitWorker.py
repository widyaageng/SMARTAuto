from unittest import TestCase
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

class LimitWorker(object):
    
    def __init__(self):
        self.DUTName = input("Enter UUT Type, case- and space-sensitive:\n")
        self.UUTSubType = input(
            "Enter UUT Subtype according to smart system master database, case- and space-sensitive:\n")
        self.TestLimitVersions = input("Test Limit Version (integer only):\n")

        self.smartweb = f"http://rws01442418/SMART/ManageTestLimits"
        self.driverPath = os.path.join(str(Path.cwd()), 'msedgedriver.exe')
        self.driver = webdriver.Edge(executable_path=self.driverPath)

        self.paramName = []
        self.SQLParamHTMLScan = []
        self.testParamDictList = []
        self.groupId = ''


    """ Navigate and pull the limit of UUT """
    def selectUUTLimitTable(self):
        self.driver.get(self.smartweb)
        elem = self.driver.find_element_by_xpath(f"//select[contains(@name, 'toolType')]")
        if self.DUTName in elem.text.split("\n"):
            selectElem = Select(elem)
            selectElem.select_by_visible_text(self.DUTName)
        else:
            raise Exception("UUT Type is not valid/mismatch with any database DUT!")
        
        time.sleep(2)
        elem = self.driver.find_element_by_xpath(f"//select[contains(@name, 'toolSubType')]")
        if self.UUTSubType in elem.text.split("\n"):
            selectElem = Select(elem)
            selectElem.select_by_visible_text(self.UUTSubType)
        else:
            raise Exception("UUT Subtype Name is not valid/mismatch with any database DUT!")
        
        time.sleep(2)
        elem = self.driver.find_element_by_xpath(f"//select[contains(@name, 'toolLimitVersion')]")
        if self.TestLimitVersions in elem.text.split("\n"):
            selectElem = Select(elem)
            selectElem.select_by_visible_text(self.TestLimitVersions)
        else:
            raise Exception("UUT TestLimitVersions is not valid/mismatch with any database DUT!")
        
        time.sleep(1)
        elem = self.driver.find_element_by_xpath(f"//input[contains(@type, 'submit') and contains(@value, 'Filter')]")
        if (elem.get_attribute('id') == 'filterButton'):
            elem.click()
        else:
            raise Exception("It's not landed into Filter button!")

    def scrapeSQLParamNumber(self):
        print("Scrapping parameter name from web and SQL output...")
        elems = self.driver.find_elements_by_xpath("//tbody/tr/td/a[contains(@href, '&tempGroupId=') or contains(@href, '&limitsId=')]")

        SQLParamHTMLScan = []

        paramName = [e.find_element_by_xpath("../../td/following-sibling::td[1]").text for e in elems]
        paramHTML = [e.get_attribute('href') for e in elems]

        try:
            for elem in paramHTML:
                tempParamNumber = re.match('.*(&parameter=\d+)&tempGroupId=\d+$', elem)
                if tempParamNumber is None:
                    tempParamNumber = re.match('.*testLimitVersion=\d+(&limitsId=\d+)$', elem).groups()[0]
                else:
                    tempParamNumber = tempParamNumber.groups()[0]
                SQLParamHTMLScan.append(tempParamNumber)
        except:
            raise IndexError('Regex group index is out of range: Invalid number from href')
        
        if True in (paramNum == None for paramNum in SQLParamHTMLScan):
            raise Exception('Some edit anchor links are not detected, refresh chrome driver or check page loading')

        print("Scrapping done!")
        self.paramName = paramName
        self.SQLParamHTMLScan = SQLParamHTMLScan

    def flatten(self, xs):
        result = []
        if isinstance(xs, (list, tuple)):
            for x in xs:
                result.extend(self.flatten(x))
        else:
            result.append(xs)
        return result

    def extractParameterLimit(self):

        print("Extracting table from web...")
        # Navigate to limit webpage
        self.selectUUTLimitTable()

        # Retrieve table elements
        elems = self.driver.find_elements_by_xpath("//tbody/tr/td/a[contains(@href, '&tempGroupId=') or contains(@href, '&limitsId=')]")
        paramParentName = [e.find_element_by_xpath("../../td").text for e in elems]
        paramName = [e.find_element_by_xpath("../../td/following-sibling::td[1]").text for e in elems]
        paramLimitsLo = [e.find_element_by_xpath("../../td/following-sibling::td[2]").text for e in elems]
        paramLimitsHi = [e.find_element_by_xpath("../../td/following-sibling::td[3]").text for e in elems]
        paramUnit = [e.find_element_by_xpath("../../td/following-sibling::td[4]").text for e in elems]
        paramtempGroup = [e.find_element_by_xpath("../../td/following-sibling::td[5]").text for e in elems]
        
        tempArr = []
        for item in paramParentName:
            if item!='':
                tempItem = item
                tempArr.append(item)
            else:
                tempArr.append(tempItem)
        
        paramParentName = tempArr
        del tempArr, tempItem

        # Check equal length as these td elems are put in rows
        isEqualLength = list(set({
            len(paramParentName),
            len(paramName),
            len(paramLimitsLo),
            len(paramLimitsHi),
            len(paramUnit),
            len(paramtempGroup)}))[0] == len(paramParentName)

        if isEqualLength:
            pass
        else:
            raise AssertionError("Param details from web scrap do not have the same length")

        ################################ Create ini file data structure ################################
        config = configparser.RawConfigParser()
        tempDict = OrderedDict(zip(paramParentName, ['' for i in paramParentName]))

        # Testgroup section
        uniqueTestCase = {i:tempDict[i] for i in tempDict.keys()}
        config['TESTGROUP'] = uniqueTestCase
        
        # Entry section ambient
        for tupleItem in zip(
            paramParentName,
            paramName,
            paramLimitsLo,
            paramLimitsHi,
            paramUnit,
            paramtempGroup):
            if tupleItem[5] == 'Ambient':
                try:
                    if config[tupleItem[0]][tupleItem[1]] != '':
                        config.set(tupleItem[0], tupleItem[1],','.join([str(tupleItem[4]),'LimitType', 'ParamNumber', 'True', tupleItem[2], tupleItem[3]] + config[tupleItem[0]][tupleItem[1]].split(',')))
                except KeyError:
                    try:
                        config.add_section(tupleItem[0])
                    except configparser.DuplicateSectionError:
                        # let go duplicate error only
                        pass
                    config.set(tupleItem[0], tupleItem[1], ','.join([str(tupleItem[4]),'LimitType', 'ParamNumber', 'True', tupleItem[2], tupleItem[3]]))
            else:
                continue

        for tupleItem in zip(
            paramParentName,
            paramName,
            paramLimitsLo,
            paramLimitsHi,
            paramUnit,
            paramtempGroup):
            if tupleItem[5] == 'Hot':
                try:
                    if config[tupleItem[0]][tupleItem[1]] != '':
                        config.set(tupleItem[0], tupleItem[1],','.join(config[tupleItem[0]][tupleItem[1]].split(',') + [tupleItem[2], tupleItem[3]]))
                except KeyError:
                    try:
                        config.add_section(tupleItem[0])
                    except configparser.DuplicateSectionError:
                        # let go duplicate error only
                        pass
                    config.set(tupleItem[0], tupleItem[1], ','.join([tupleItem[2], tupleItem[3]]))
            else:
                continue

        for tupleItem in zip(
            paramParentName,
            paramName,
            paramLimitsLo,
            paramLimitsHi,
            paramUnit,
            paramtempGroup):
            if tupleItem[5] == 'Cold':
                try:
                    if config[tupleItem[0]][tupleItem[1]] != '':
                        config.set(tupleItem[0], tupleItem[1],','.join(config[tupleItem[0]][tupleItem[1]].split(',') + [tupleItem[2], tupleItem[3]]))
                except KeyError:
                    try:
                        config.add_section(tupleItem[0])
                    except configparser.DuplicateSectionError:
                        # let go duplicate error only
                        pass
                    config.set(tupleItem[0], tupleItem[1], ','.join([tupleItem[2], tupleItem[3]]))
            else:
                continue

        
        filename = input("Enter ini filename to be generated (without .ini):\n")
        with open(f"{filename}.ini", 'w') as configFILE:
            config.write(configFILE)
        
        print(f"Extraction done, check file with name {filename}.ini in the same folder as this file")

    def createParamLimit(self):
        filename = input("Enter ini filepath reference for limit creation without .ini extension:\n")
        config = configparser.ConfigParser()
        config.read(f"{filename}.ini")

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

        mainTest = self.flatten(mainTest)

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

        self.groupId = groupId
        self.testParamDictList = testParamDict

        print(f"Parameter testParamDictList is ready to be written!")
    
    def addParamToDB(self, index):

        PFEvaluatedParam = [i for i in self.testParamDictList if i['PF Evaluated']=='True']
        assert self.paramName[index]==PFEvaluatedParam[index % len(PFEvaluatedParam)]['Parameter'], "Parameter name mismatch!"

        elem = self.driver.find_element_by_xpath(f"//a[contains(@href, '{self.SQLParamHTMLScan[index]}')]")
        if (elem.text == 'Add to DB'):
            elem.click()
        else:
            raise Exception("It's not landed into Add to DB anchor!")        

        thermalGroup = self.driver.find_element_by_xpath(f"//div[contains(@class, 'form-group')]/label[contains(@for, 'TempGroupId')]/following-sibling::div").text
        
        elem = self.driver.find_element_by_xpath(f"//input[contains(@name, 'LowLimit')]")
        if (elem.get_attribute('id') == 'LowLimit'):
            elem.clear()
            elem.send_keys(PFEvaluatedParam[index % len(PFEvaluatedParam)][thermalGroup + 'Limit'][0])
        else:
            raise Exception("It's not landed into Low Limit field")
        
        elem = self.driver.find_element_by_xpath(f"//input[contains(@name, 'HighLimit')]")
        if (elem.get_attribute('id') == 'HighLimit'):
            elem.clear()
            elem.send_keys(PFEvaluatedParam[index % len(PFEvaluatedParam)][thermalGroup + 'Limit'][1])
        else:
            raise Exception("It's not landed into High Limit field")
        
        elem = self.driver.find_element_by_xpath(f"//input[contains(@type, 'submit')]")
        if (elem.get_attribute('value') == 'Create'):
            elem.click()
        else:
            raise Exception("It's not landed into Create button!")
    

    def editParamToDB(self, index):

        PFEvaluatedParam = [i for i in self.testParamDictList if i['PF Evaluated']=='True']
        assert self.paramName[index]==PFEvaluatedParam[index % len(PFEvaluatedParam)]['Parameter'], "Parameter name mismatch!"

        elem = self.driver.find_element_by_xpath(f"//a[contains(@href, '{self.SQLParamHTMLScan[index]}')]")
        if (elem.text == 'Edit'):
            elem.click()
        else:
            raise Exception("It's not landed into Edit anchor!")        

        thermalGroup = self.driver.find_element_by_xpath(f"//div[contains(@class, 'form-group')]/label[contains(@for, 'TempGroupId')]/following-sibling::div").text

        elem = self.driver.find_element_by_xpath(f"//input[contains(@name, 'LowLimit')]")
        if (elem.get_attribute('id') == 'LowLimit'):
            elem.clear()
            elem.send_keys(PFEvaluatedParam[index % len(PFEvaluatedParam)][thermalGroup + 'Limit'][0])
        else:
            raise Exception("It's not landed into Low Limit field")
        
        elem = self.driver.find_element_by_xpath(f"//input[contains(@name, 'HighLimit')]")
        if (elem.get_attribute('id') == 'HighLimit'):
            elem.clear()
            elem.send_keys(PFEvaluatedParam[index % len(PFEvaluatedParam)][thermalGroup + 'Limit'][1])
        else:
            raise Exception("It's not landed into High Limit field")
        
        elem = self.driver.find_element_by_xpath(f"//input[contains(@type, 'submit')]")
        if (elem.get_attribute('value') == 'Save'):
            elem.click()
        else:
            raise Exception("It's not landed into Save button!")

    def writeLimit(self):

        assert len(self.testParamDictList) > 0, "Parameter to write is empty!"

        PFEvaluatedParam = [i for i in self.testParamDictList if i['PF Evaluated']=='True']
        assert len(PFEvaluatedParam)*2 == len(self.paramName) , "Parameter array length is not equal to web parameter name rows!"

    def goBackToList(self):
        elem = self.driver.find_element_by_xpath(f"//a[contains(text(), 'Back to List')]")
        if (elem.text == 'Back to List'):
            elem.click()
        else:
            raise Exception("It's not landed into Back to List button!")
        
    def destroy(self):
        self.driver.quit()