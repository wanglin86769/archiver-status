# EPICS PVs for Archiver Appliance status

This small tool publishes Archiver Appliance status as EPICS PVs by polling Archiver Appliance BPL metrics with HTTP/JSON data format.

## Software environment

* Python 3

* pcaspy

## PV list for single node deployment of Archiver Appliance

* MTEST:status
* MTEST:MGMT_uptime
* MTEST:pvCount
* MTEST:connectedPVCount
* MTEST:disconnectedPVCount
* MTEST:dataRateGBPerDay
* MTEST:sts_total_space
* MTEST:sts_available_space
* MTEST:sts_available_space_percent
* MTEST:mts_total_space
* MTEST:mts_available_space
* MTEST:mts_available_space_percent
* MTEST:lts_total_space
* MTEST:lts_available_space
* MTEST:lts_available_space_percent

## PV list for cluster deployment of Archiver Appliance

* MTEST:appliance_01:status
* MTEST:appliance_01:MGMT_uptime
* MTEST:appliance_01:pvCount
* MTEST:appliance_01:connectedPVCount
* MTEST:appliance_01:disconnectedPVCount
* MTEST:appliance_01:dataRateGBPerDay
* MTEST:appliance_01:sts_total_space
* MTEST:appliance_01:sts_available_space
* MTEST:appliance_01:sts_available_space_percent
* MTEST:appliance_01:mts_total_space
* MTEST:appliance_01:mts_available_space
* MTEST:appliance_01:mts_available_space_percent
* MTEST:appliance_01:lts_total_space
* MTEST:appliance_01:lts_available_space
* MTEST:appliance_01:lts_available_space_percent
* MTEST:appliance_02:status
* MTEST:appliance_02:MGMT_uptime
* MTEST:appliance_02:pvCount
* MTEST:appliance_02:connectedPVCount
* MTEST:appliance_02:disconnectedPVCount
* MTEST:appliance_02:dataRateGBPerDay
* MTEST:appliance_02:sts_total_space
* MTEST:appliance_02:sts_available_space
* MTEST:appliance_02:sts_available_space_percent
* MTEST:appliance_02:mts_total_space
* MTEST:appliance_02:mts_available_space
* MTEST:appliance_02:mts_available_space_percent
* MTEST:appliance_02:lts_total_space
* MTEST:appliance_02:lts_available_space
* MTEST:appliance_02:lts_available_space_percent

## Configuration

* For single node deployment, set *APPLIANCE_URL* and *APPLIANCE_IDENTITY* as strings.
* For cluster deployment, set *appliances* as list of dictionary.

## Screenshot for single node deployment of Archiver Appliance

![Alt text](screenshots/single_node.png?raw=true "Title")

## Screenshot for cluster deployment of Archiver Appliance

![Alt text](screenshots/cluster_node_01.png?raw=true "Title")

![Alt text](screenshots/cluster_node_02.png?raw=true "Title")

## License
MIT license