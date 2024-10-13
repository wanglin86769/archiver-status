# EPICS PVs for Archiver Appliance status

This small tool publishes Archiver Appliance status as EPICS PVs by polling Archiver Appliance BPL metrics with HTTP/JSON data format.

## Software environment

This software is developed and tested in the following environment,

* Python 3.11.1

* pcaspy 0.8.0

## Sources files

* `archiver_status_single_node.py`: it can be used for single node deployment of Archiver Appliance.

* `archiver_status_cluster.py`: it can be used for cluster deployment of Archiver Appliance.

* `archiver_status.py`: it merges the two source files above and can be used for either single node or cluster deployment.

Any of the source files above has been tested and can be used.

## Configuration

* For `archiver_status_single_node.py`, set `APPLIANCE_URL` and `APPLIANCE_IDENTITY` as strings.
* For `archiver_status_cluster.py`, set `appliances` as list of dictionary.
* For `archiver_status.py`, add one element to `appliances` for single node and multiple elements for cluster.

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

If the cluster includes two nodes with the idenntity appliance_01 and appliance_02 respectively.

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

## Screenshot for single node deployment of Archiver Appliance

Traditional CS-Studio

![Alt text](screenshots/cs-studio/single_node.png?raw=true "Title")

Phoebus

![Alt text](screenshots/phoebus/single_node.png?raw=true "Title")

## Screenshot for cluster deployment of Archiver Appliance

Traditional CS-Studio

![Alt text](screenshots/cs-studio/cluster_node_01.png?raw=true "Title")

![Alt text](screenshots/cs-studio/cluster_node_02.png?raw=true "Title")

Phoebus

![Alt text](screenshots/phoebus/cluster_node_01.png?raw=true "Title")

![Alt text](screenshots/phoebus/cluster_node_02.png?raw=true "Title")

## License
MIT license