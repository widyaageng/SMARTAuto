import os
import re
import configparser
from collections import OrderedDict
from typing import List

class DeviceGeneric(object):

    def __init__(self, configFile=None, testCaseParameterDictList={}):
        super().__init__()
        self.testGroup = None
        self.testGroupCases = None
        self._ver = None
        self.configFile = configFile
        self.configParser = None
        self.testCaseParameterDictList = testCaseParameterDictList

    @property
    def testCaseParameterDictList(self):
        return self._testCaseParamDictList

    @testCaseParameterDictList.setter
    def testCaseParameterDictList(self, newTestCaseParam):
        """ To validate newTestCaseParameter type"""

        if newTestCaseParam is None or len(newTestCaseParam) == 0:
            self._testCaseParamDictList = {}
            return self._testCaseParamDictList

        assert isinstance(
            newTestCaseParam, list), "ToolsTypeDUT.py: New params must be list of OrderedDict"
        self._testCaseParamDictList = newTestCaseParam
        return self._testCaseParamDictList

    @property
    def configFile(self):
        return self._configFile
    
    @configFile.setter
    def configFile(self, filepath):

        """ To check if file exists """
        try:
            with open(filepath, 'r') as fpath:
                print(f"Opening {fpath.readline()}")
        except Exception as e:
            raise f"Cant open file {filepath}"

        self._configFile = filepath
        
        return self._configFile

    def readConfigFile(self):
        """ To read configfile from attribute configfile """
        raise NotImplementedError

    def syncTestParamConfig(self):
        """ To update testparamdict from configfile """
        raise NotImplementedError

    def updateSingleParam(self, newParamDict, section, param):
        """ To update single parameter """
        raise NotImplementedError

    def updateAllParam(self):
        """ Update object parameter based on revised ini file """
        raise NotImplementedError


class DeviceUnderTest(DeviceGeneric):
    def __init__(self, configFile=None, configParser=None, groupId=[]):
        super().__init__(configFile)
        self.configParser = configParser
        self.groupId = groupId

    @property
    def configParser(self):
        return self._configParser

    @configParser.setter
    def configParser(self, newConfigParser):
        if newConfigParser is None:
            self._configParser = configparser.ConfigParser()
        else:
            assert isinstance(
                newConfigParser, configparser.ConfigParser), "New parser is not ConfigParser type"
            self._configParser = newConfigParser
            return self._configParser

    def readConfigFile(self):
        print(f"\nReading {self.configFile}...")
        try:
            self.configParser.read(self.configFile)
        except Exception as e:
            raise f"Error reading config file, reason: {e}"
        print(f"\nReading {self.configFile} is successful!\n")

    def syncTestParamConfig(self) -> List[OrderedDict]:

        print(f"\nSyncing Object using {self.configFile}...")
        self.readConfigFile()
        
        try:
            testCaseRaw = [i for i in self.configParser['TESTGROUP']]
            mainTest = [self.configParser['TESTGROUP'][i].split(",") for i in testCaseRaw]
        except:
            raise f"ConfigParser do not have section TESTGROUP or /ini file having invalid values"

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
        tempDict = {}
        testParamDict = []

        for i in mainTest:
            tempDict = OrderedDict(zip(self.configParser[i].keys(), self.configParser[i].values()))
            for j, key in enumerate(tempDict.keys()):
                self.groupId.append(tempDict['Group Id'])
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
                    
                    """ To include cold limits if any """
                    if len(tempArgs)==8:
                        testParamDict[-1]['ColdLimit'] = [tempArgs[6], tempArgs[7]]

                    """ To include hot limits if any """
                    if len(tempArgs)==10:
                        testParamDict[-1]['HotLimit'] = [tempArgs[8], tempArgs[9]]

        self.groupId = list(set(self.groupId))
        self.groupId.sort()
        self.testCaseParameterDictList = testParamDict
        print(f"\Syncing Object completed!")

        return self.testCaseParameterDictList

    def updateSingleParam(self, section, param, values: list) -> None:
        try:
            assert len(values) >= 6, "Update values must follow structure: <Unit>,<LimitType>,<Param#>,<Pass/Fail>,<ambient lo>,<ambient hi>,<optional-cold limit>, <optional-hi limit>"
            self.configParser[section][param] = values
            with open(self.configFile, 'w') as filepath:
                self.configParser.write(filepath)
        except:
            raise f"Updating parameter is failed, check if section and parameter exist and check values. R/W access"

    def updateAllParam(self) -> configparser.ConfigParser:
        self.readConfigFile(self)
        self.syncTestParamConfig(self)
        return self.configParser

    """ Utils """
    def flatten(self, nestediters):
        result = []
        if isinstance(nestediters, (list, tuple)):
            for x in nestediters:
                result.extend(self.flatten(x))
        else:
            result.append(nestediters)
        return result
