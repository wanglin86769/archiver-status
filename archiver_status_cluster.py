#!/usr/bin/env python
import threading
import time
import requests
import json
import pprint

from pcaspy import Driver, SimpleServer, Alarm, Severity
from requests.exceptions import Timeout
from requests.exceptions import ConnectionError

# Configuration
appliances = [ # All the appliances in the cluster
    { 'url': 'http://10.1.236.142:17665', 'identity': 'appliance_01' },
    { 'url': 'http://10.1.236.143:17665', 'identity': 'appliance_02' },
]
REQUEST_TIMEOUT = 5
REQUEST_INTERVAL = 5
prefix = 'MTEST:'

print('\n')
print('*** This tool is used to monitor status of Archiver Appliance deployed as cluster ***')
print('*** All nodes in the cluster are as below ***')
for appliance in appliances:
    pprint.pprint(appliance)
print('\n')

# Build PVs for Archiver Appliance status
pvdb = {}
for appliance in appliances:
    # Each appliance has the following PVs
    identity = appliance['identity']
    pvdb[f'{identity}:status']                      = { 'type': 'string', 'value': '' }
    pvdb[f'{identity}:MGMT_uptime']                 = { 'type': 'string', 'value': '' }
    pvdb[f'{identity}:pvCount']                     = { 'type': 'int', 'value': 0 }
    pvdb[f'{identity}:connectedPVCount']            = { 'type': 'int', 'value': 0 }
    pvdb[f'{identity}:disconnectedPVCount']         = { 'type': 'int', 'value': 0 }
    pvdb[f'{identity}:pausedPVCount']               = { 'type': 'int', 'value': 0 }
    pvdb[f'{identity}:dataRateGBPerDay']            = { 'type': 'float', 'prec': 2, 'unit': 'GB/day', 'value': 0 }
    pvdb[f'{identity}:sts_total_space']             = { 'type': 'float', 'prec': 2, 'unit': 'GB', 'value': 0 }
    pvdb[f'{identity}:sts_available_space']         = { 'type': 'float', 'prec': 2, 'unit': 'GB', 'value': 0 }
    pvdb[f'{identity}:sts_available_space_percent'] = { 'type': 'float', 'prec': 2, 'unit': '%', 'value': 0 }
    pvdb[f'{identity}:mts_total_space']             = { 'type': 'float', 'prec': 2, 'unit': 'GB', 'value': 0 }
    pvdb[f'{identity}:mts_available_space']         = { 'type': 'float', 'prec': 2, 'unit': 'GB', 'value': 0 }
    pvdb[f'{identity}:mts_available_space_percent'] = { 'type': 'float', 'prec': 2, 'unit': '%', 'value': 0 }
    pvdb[f'{identity}:lts_total_space']             = { 'type': 'float', 'prec': 2, 'unit': 'GB', 'value': 0 }
    pvdb[f'{identity}:lts_available_space']         = { 'type': 'float', 'prec': 2, 'unit': 'GB', 'value': 0 }
    pvdb[f'{identity}:lts_available_space_percent'] = { 'type': 'float', 'prec': 2, 'unit': '%', 'value': 0 }

print('\n')
print('*** The following PVs will be generated ***')
for key, value in pvdb.items():
    print(f'{prefix}{key}')
print('\n')
 
class myDriver(Driver):
    def __init__(self):
        Driver.__init__(self)
        # Create three polling threads for each appliance
        for appliance in appliances:
            self.tid = threading.Thread(target = self.pollInstanceMetrics, args = (appliance,)) 
            self.tid.daemon = True
            self.tid.start()
            self.tid = threading.Thread(target = self.pollApplianceMetrics, args = (appliance,)) 
            self.tid.daemon = True
            self.tid.start()
            self.tid = threading.Thread(target = self.pollStorageMetrics, args = (appliance,)) 
            self.tid.daemon = True
            self.tid.start()

    # Set alarm and invalid value for instance metrics
    def invalidateInstanceMetrics(self, appliance):
        identity = appliance["identity"]
        self.setParam(f'{identity}:status', 'Disconnected')
        self.setParam(f'{identity}:MGMT_uptime', 'Unknown')
        self.setParam(f'{identity}:pvCount', 0)
        self.setParam(f'{identity}:connectedPVCount', 0)
        self.setParam(f'{identity}:disconnectedPVCount', 0)
        self.setParam(f'{identity}:dataRateGBPerDay', 0)
        self.setParamStatus(f'{identity}:status', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus(f'{identity}:MGMT_uptime', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus(f'{identity}:pvCount', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus(f'{identity}:connectedPVCount', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus(f'{identity}:disconnectedPVCount', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus(f'{identity}:dataRateGBPerDay', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.updatePVs()

    # Set alarm and invalid value for appliance metrics
    def invalidateApplianceMetrics(self, appliance):
        identity = appliance["identity"]
        self.setParam(f'{identity}:pausedPVCount', 0)
        self.setParamStatus(f'{identity}:pausedPVCount', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.updatePVs()

    # Set alarm and invalid value for storage metrics
    def invalidateStorageMetrics(self, appliance):
        identity = appliance["identity"]
        self.setParam(f'{identity}:sts_total_space', 0)
        self.setParam(f'{identity}:sts_available_space', 0)
        self.setParam(f'{identity}:sts_available_space_percent', 0)
        self.setParam(f'{identity}:mts_total_space', 0)
        self.setParam(f'{identity}:mts_available_space', 0)
        self.setParam(f'{identity}:mts_available_space_percent', 0)
        self.setParam(f'{identity}:lts_total_space', 0)
        self.setParam(f'{identity}:lts_available_space', 0)
        self.setParam(f'{identity}:lts_available_space_percent', 0)
        self.setParamStatus(f'{identity}:sts_total_space', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus(f'{identity}:sts_available_space', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus(f'{identity}:sts_available_space_percent', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus(f'{identity}:mts_total_space', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus(f'{identity}:mts_available_space', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus(f'{identity}:mts_available_space_percent', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus(f'{identity}:lts_total_space', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus(f'{identity}:lts_available_space', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus(f'{identity}:lts_available_space_percent', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.updatePVs()

    # Polling thread for instance metrics
    def pollInstanceMetrics(self, appliance):
        url = appliance["url"]
        identity = appliance["identity"]
        GET_INSTANCE_METRICS_URL = f'{url}/mgmt/bpl/getInstanceMetrics'

        while True:
            try:
                # Get instance metrics data
                response = requests.get(GET_INSTANCE_METRICS_URL, timeout = REQUEST_TIMEOUT)

                if response.status_code < 200 or response.status_code >= 300:
                    print('Appliance ' + identity + ': ' + 'Bad response status code ' + str(response.status_code) + ' for instance metrics data')
                    self.invalidateInstanceMetrics(appliance)
                    time.sleep(REQUEST_INTERVAL)
                    continue

                text = response.text
                dataList = json.loads(text)

                found = False
                for item in dataList:
                    if 'instance' in item and item['instance'] == identity:
                        data = item
                        found = True
                        break
                
                if not found:
                    print(f'Appliance {identity}: Instance data is not found')
                    self.invalidateInstanceMetrics(appliance)
                    time.sleep(REQUEST_INTERVAL)
                    continue

                if not('status' in data):
                    print(f'Appliance {identity}: Instance metrics data does not include status')
                    self.invalidateInstanceMetrics(appliance)
                    time.sleep(REQUEST_INTERVAL)
                    continue

                if not('MGMT_uptime' in data):
                    print(f'Appliance {identity}: Instance metrics data does not include MGMT_uptime')
                    self.invalidateInstanceMetrics(appliance)
                    time.sleep(REQUEST_INTERVAL)
                    continue

                if not('pvCount' in data):
                    print(f'Appliance {identity}: Instance metrics data does not include pvCount')
                    self.invalidateInstanceMetrics(appliance)
                    time.sleep(REQUEST_INTERVAL)
                    continue

                if not('connectedPVCount' in data):
                    print(f'Appliance {identity}: Instance metrics data does not include connectedPVCount')
                    self.invalidateInstanceMetrics(appliance)
                    time.sleep(REQUEST_INTERVAL)
                    continue

                if not('disconnectedPVCount' in data):
                    print(f'Appliance {identity}: Instance metrics data does not include disconnectedPVCount')
                    self.invalidateInstanceMetrics(appliance)
                    time.sleep(REQUEST_INTERVAL)
                    continue

                status = data['status']  # string
                MGMT_uptime = data['MGMT_uptime']  # string
                pvCount = int(data['pvCount'])  # int
                connectedPVCount = int(data['connectedPVCount'])  # int
                disconnectedPVCount = int(data['disconnectedPVCount'])  # int
                dataRateGBPerDay = float(data['dataRateGBPerDay'])  # float

                # print(status)
                # print(MGMT_uptime)
                # print(pvCount)
                # print(connectedPVCount)
                # print(disconnectedPVCount)
                # print(dataRateGBPerDay)

                self.setParam(f'{identity}:status', status)
                self.setParam(f'{identity}:MGMT_uptime', MGMT_uptime)
                self.setParam(f'{identity}:pvCount', pvCount)
                self.setParam(f'{identity}:connectedPVCount', connectedPVCount)
                self.setParam(f'{identity}:disconnectedPVCount', disconnectedPVCount)
                self.setParam(f'{identity}:dataRateGBPerDay', dataRateGBPerDay)

                # do updates so clients see the changes
                self.updatePVs()

            except Timeout:
                print(f'Appliance {identity}: Request for instance metrics data has timed out')
                self.invalidateInstanceMetrics(appliance)

            except ConnectionError:
                print(f'Appliance {identity}: Connection for instance metrics data has been refused')
                self.invalidateInstanceMetrics(appliance)

            # Delay 5 seconds
            time.sleep(REQUEST_INTERVAL)

    # Polling thread for appliance metrics
    def pollApplianceMetrics(self, appliance):
        url = appliance["url"]
        identity = appliance["identity"]
        GET_APPLIANCE_METRICS_FOR_APPLIANCE_URL = f'{url}/mgmt/bpl/getApplianceMetricsForAppliance?appliance={identity}'

        while True:
            try: 
                # Get storage metrics data
                response = requests.get(GET_APPLIANCE_METRICS_FOR_APPLIANCE_URL, timeout = REQUEST_TIMEOUT)

                if response.status_code < 200 or response.status_code >= 300:
                    print('Appliance ' + identity + ': ' + 'Bad response status code ' + str(response.status_code) + ' for appliance metrics data')
                    self.invalidateApplianceMetrics(appliance)
                    time.sleep(REQUEST_INTERVAL)
                    continue

                text = response.text

                if not text:
                    print('Appliance ' + identity + ': ' + 'response text for appliance metrics data is empty, maybe identity is not correct')
                    self.invalidateApplianceMetrics(appliance)
                    time.sleep(REQUEST_INTERVAL)
                    continue

                data = json.loads(text)

                if len(data) == 0:
                    print(f'Appliance {identity}: Empty text response for appliance metrics data')
                    self.invalidateApplianceMetrics(appliance)
                    time.sleep(REQUEST_INTERVAL)
                    continue

                for item in data:
                    if item['name'] == 'Paused PV count':
                        pausedPVCount = int(item['value'])

                # print(pausedPVCount)
                        
                self.setParam(f'{identity}:pausedPVCount', pausedPVCount)
            
                # do updates so clients see the changes
                self.updatePVs()

            except Timeout:
                print(f'Appliance {identity}: Request for appliance metrics data has timed out')
                self.invalidateApplianceMetrics(appliance)
                
            except ConnectionError:
                print(f'Appliance {identity}: Connection for appliance metrics data has been refused')
                self.invalidateApplianceMetrics(appliance)

            # Delay 5 seconds
            time.sleep(REQUEST_INTERVAL)

    # Polling thread for storage metrics
    def pollStorageMetrics(self, appliance):
        url = appliance["url"]
        identity = appliance["identity"]
        GET_STORAGE_METRICS_FOR_APPLIANCE_URL = f'{url}/mgmt/bpl/getStorageMetricsForAppliance?appliance={identity}'

        while True:
            try: 
                # Get storage metrics data
                response = requests.get(GET_STORAGE_METRICS_FOR_APPLIANCE_URL, timeout = REQUEST_TIMEOUT)

                if response.status_code < 200 or response.status_code >= 300:
                    print('Appliance ' + identity + ': ' + 'Bad response status code ' + str(response.status_code) + ' for storage metrics data')
                    self.invalidateStorageMetrics(appliance)
                    time.sleep(REQUEST_INTERVAL)
                    continue

                text = response.text

                if not text:
                    print('Appliance ' + identity + ': ' + 'response text for storage metrics data is empty, maybe identity is not correct')
                    self.invalidateStorageMetrics(appliance)
                    time.sleep(REQUEST_INTERVAL)
                    continue

                data = json.loads(text)

                if len(data) == 0:
                    print(f'Appliance {identity}: Empty text response for storage metrics data')
                    self.invalidateStorageMetrics(appliance)
                    time.sleep(REQUEST_INTERVAL)
                    continue

                for item in data:
                    if item['name'] == 'STS':
                        sts_total_space = float(item['total_space'].replace(',', ''))
                        sts_available_space = float(item['available_space'].replace(',', ''))
                        sts_available_space_percent = float(item['available_space_percent'].replace(',', ''))
                    if item['name'] == 'MTS':
                        mts_total_space = float(item['total_space'].replace(',', ''))
                        mts_available_space = float(item['available_space'].replace(',', ''))
                        mts_available_space_percent = float(item['available_space_percent'].replace(',', ''))
                    if item['name'] == 'LTS':
                        lts_total_space = float(item['total_space'].replace(',', ''))
                        lts_available_space = float(item['available_space'].replace(',', ''))
                        lts_available_space_percent = float(item['available_space_percent'].replace(',', ''))

                # print(sts_total_space)
                # print(sts_available_space)
                # print(sts_available_space_percent)
                # print(mts_total_space)
                # print(mts_available_space)
                # print(mts_available_space_percent)
                # print(lts_total_space)
                # print(lts_available_space)
                # print(lts_available_space_percent)
                        
                self.setParam(f'{identity}:sts_total_space', sts_total_space)
                self.setParam(f'{identity}:sts_available_space', sts_available_space)
                self.setParam(f'{identity}:sts_available_space_percent', sts_available_space_percent)
                self.setParam(f'{identity}:mts_total_space', mts_total_space)
                self.setParam(f'{identity}:mts_available_space', mts_available_space)
                self.setParam(f'{identity}:mts_available_space_percent', mts_available_space_percent)
                self.setParam(f'{identity}:lts_total_space', lts_total_space)
                self.setParam(f'{identity}:lts_available_space', lts_available_space)
                self.setParam(f'{identity}:lts_available_space_percent', lts_available_space_percent)
            
                # do updates so clients see the changes
                self.updatePVs()

            except Timeout:
                print(f'Appliance {identity}: Request for storage metrics data has timed out')
                self.invalidateStorageMetrics(appliance)
                
            except ConnectionError:
                print(f'Appliance {identity}: Connection for storage metrics data has been refused')
                self.invalidateStorageMetrics(appliance)

            # Delay 5 seconds
            time.sleep(REQUEST_INTERVAL)

if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while True:
        server.process(0.1)
