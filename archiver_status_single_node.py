#!/usr/bin/env python
import threading
import time
import requests
import json

from pcaspy import Driver, SimpleServer, Alarm, Severity
from requests.exceptions import Timeout
from requests.exceptions import ConnectionError

# Configuration
APPLIANCE_URL = 'http://localhost:17665'
APPLIANCE_IDENTITY = 'appliance0'
REQUEST_TIMEOUT = 5
REQUEST_INTERVAL = 5
prefix = 'MTEST:'

print('\n')
print('*** This tool is used to monitor status of Archiver Appliance deployed as single node ***')
print('*** The URL and identity of the node is as below ***')
print(f'URL: {APPLIANCE_URL}')
print(f'identity: {APPLIANCE_IDENTITY}')
print('\n')

GET_INSTANCE_METRICS_URL = f'{APPLIANCE_URL}/mgmt/bpl/getInstanceMetrics'
GET_STORAGE_METRICS_FOR_APPLIANCE_URL = f'{APPLIANCE_URL}/mgmt/bpl/getStorageMetricsForAppliance?appliance={APPLIANCE_IDENTITY}'

pvdb = {
        'status':                       { 'type': 'string', 'value': '' },
        'MGMT_uptime':                  { 'type': 'string', 'value': '' },
        'pvCount':                      { 'type': 'int', 'value': 0 },
        'connectedPVCount':             { 'type': 'int', 'value': 0 },
        'disconnectedPVCount':          { 'type': 'int', 'value': 0 },
        'dataRateGBPerDay':             { 'type': 'float', 'prec': 2, 'unit': 'GB/day', 'value': 0 },
        'sts_total_space':              { 'type': 'float', 'prec': 2, 'unit': 'GB', 'value': 0 },
        'sts_available_space':          { 'type': 'float', 'prec': 2, 'unit': 'GB', 'value': 0 },
        'sts_available_space_percent':  { 'type': 'float', 'prec': 2, 'unit': '%', 'value': 0 },
        'mts_total_space':              { 'type': 'float', 'prec': 2, 'unit': 'GB', 'value': 0 },
        'mts_available_space':          { 'type': 'float', 'prec': 2, 'unit': 'GB', 'value': 0 },
        'mts_available_space_percent':  { 'type': 'float', 'prec': 2, 'unit': '%', 'value': 0 },
        'lts_total_space':              { 'type': 'float', 'prec': 2, 'unit': 'GB', 'value': 0 },
        'lts_available_space':          { 'type': 'float', 'prec': 2, 'unit': 'GB', 'value': 0 },
        'lts_available_space_percent':  { 'type': 'float', 'prec': 2, 'unit': '%', 'value': 0 },
}

print('\n')
print('*** The following PVs will be generated ***')
for key, value in pvdb.items():
    print(f'{prefix}{key}')
print('\n')
 
class myDriver(Driver):
    def __init__(self):
        Driver.__init__(self)
        # Create two polling threads for the appliance
        self.tid = threading.Thread(target = self.pollInstanceMetrics) 
        self.tid.daemon = True
        self.tid.start()
        self.tid = threading.Thread(target = self.pollStorageMetrics) 
        self.tid.daemon = True
        self.tid.start()

    # Set alarm and invalid value for instance metrics
    def invalidateInstanceMetrics(self):
        self.setParam('status', 'Disconnected')
        self.setParam('MGMT_uptime', 'Unknown')
        self.setParam('pvCount', 0)
        self.setParam('connectedPVCount', 0)
        self.setParam('disconnectedPVCount', 0)
        self.setParam('dataRateGBPerDay', 0)
        self.setParamStatus('status', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus('MGMT_uptime', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus('pvCount', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus('connectedPVCount', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus('disconnectedPVCount', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus('dataRateGBPerDay', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.updatePVs()

    # Set alarm and invalid value for storage metrics
    def invalidateStorageMetrics(self):
        self.setParam('sts_total_space', 0)
        self.setParam('sts_available_space', 0)
        self.setParam('sts_available_space_percent', 0)
        self.setParam('mts_total_space', 0)
        self.setParam('mts_available_space', 0)
        self.setParam('mts_available_space_percent', 0)
        self.setParam('lts_total_space', 0)
        self.setParam('lts_available_space', 0)
        self.setParam('lts_available_space_percent', 0)
        self.setParamStatus('sts_total_space', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus('sts_available_space', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus('sts_available_space_percent', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus('mts_total_space', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus('mts_available_space', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus('mts_available_space_percent', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus('lts_total_space', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus('lts_available_space', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.setParamStatus('lts_available_space_percent', Alarm.COMM_ALARM, Severity.MINOR_ALARM)
        self.updatePVs()

    # Polling thread for instance metrics
    def pollInstanceMetrics(self):
        while True:
            try:
                # Get instance metrics data
                response = requests.get(GET_INSTANCE_METRICS_URL, timeout = REQUEST_TIMEOUT)

                if response.status_code < 200 or response.status_code >= 300:
                    print('Bad response status code ' + str(response.status_code) + ' for instance metrics data')
                    self.invalidateInstanceMetrics()
                    time.sleep(REQUEST_INTERVAL)
                    continue

                text = response.text
                data = json.loads(text)[0]

                if not('status' in data):
                    print('Instance metrics data does not include status')
                    self.invalidateInstanceMetrics()
                    time.sleep(REQUEST_INTERVAL)
                    continue

                if not('MGMT_uptime' in data):
                    print('Instance metrics data does not include MGMT_uptime')
                    self.invalidateInstanceMetrics()
                    time.sleep(REQUEST_INTERVAL)
                    continue

                if not('pvCount' in data):
                    print('Instance metrics data does not include pvCount')
                    self.invalidateInstanceMetrics()
                    time.sleep(REQUEST_INTERVAL)
                    continue

                if not('connectedPVCount' in data):
                    print('Instance metrics data does not include connectedPVCount')
                    self.invalidateInstanceMetrics()
                    time.sleep(REQUEST_INTERVAL)
                    continue

                if not('disconnectedPVCount' in data):
                    print('Instance metrics data does not include disconnectedPVCount')
                    self.invalidateInstanceMetrics()
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

                self.setParam('status', status)
                self.setParam('MGMT_uptime', MGMT_uptime)
                self.setParam('pvCount', pvCount)
                self.setParam('connectedPVCount', connectedPVCount)
                self.setParam('disconnectedPVCount', disconnectedPVCount)
                self.setParam('dataRateGBPerDay', dataRateGBPerDay)

                # do updates so clients see the changes
                self.updatePVs()

            except Timeout:
                print('Request for instance metrics data has timed out')
                self.invalidateInstanceMetrics()

            except ConnectionError:
                print('Connection for instance metrics data has been refused')
                self.invalidateInstanceMetrics()

            # Delay 5 seconds
            time.sleep(REQUEST_INTERVAL)

    # Polling thread for storage metrics
    def pollStorageMetrics(self):
        while True:
            try: 
                # Get storage metrics data
                response = requests.get(GET_STORAGE_METRICS_FOR_APPLIANCE_URL, timeout = REQUEST_TIMEOUT)

                if response.status_code < 200 or response.status_code >= 300:
                    print('Bad response status code ' + str(response.status_code) + ' for storage metrics data')
                    self.invalidateStorageMetrics()
                    time.sleep(REQUEST_INTERVAL)
                    continue

                text = response.text
                data = json.loads(text)

                if len(data) == 0:
                    print('Empty text response for storage metrics data')
                    self.invalidateStorageMetrics()
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
                        
                self.setParam('sts_total_space', sts_total_space)
                self.setParam('sts_available_space', sts_available_space)
                self.setParam('sts_available_space_percent', sts_available_space_percent)
                self.setParam('mts_total_space', mts_total_space)
                self.setParam('mts_available_space', mts_available_space)
                self.setParam('mts_available_space_percent', mts_available_space_percent)
                self.setParam('lts_total_space', lts_total_space)
                self.setParam('lts_available_space', lts_available_space)
                self.setParam('lts_available_space_percent', lts_available_space_percent)
            
                # do updates so clients see the changes
                self.updatePVs()

            except Timeout:
                print('Request for storage metrics data has timed out')
                self.invalidateStorageMetrics()
                
            except ConnectionError:
                print('Connection for storage metrics data has been refused')
                self.invalidateStorageMetrics()

            # Delay 5 seconds
            time.sleep(REQUEST_INTERVAL)

if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while True:
        server.process(0.1)
