# Customized Configurations
appliances = [
    # For single node deployment of Archiver Appliance, configure url and identity for the node
    { 'url': 'http://localhost:17665', 'identity': 'appliance0' },
    # For cluster deployment of Archiver Appliance, configure url and identity for all the nodes
    # { 'url': 'http://10.1.236.142:17665', 'identity': 'appliance_01' },
    # { 'url': 'http://10.1.236.143:17665', 'identity': 'appliance_02' },
]
REQUEST_TIMEOUT = 10
REQUEST_INTERVAL = 10
prefix = 'arcapp-acc:'
