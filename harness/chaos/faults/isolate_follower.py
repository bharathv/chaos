from time import sleep
from sh import ssh
import logging

logger = logging.getLogger("chaos")

class IsolateFollowerFault:
    def __init__(self):
        self.fault_type = "RECOVERABLE"
        self.follower = None
        self.rest = []
        self.name = "isolate follower"

    def inject(self, scenario):
        controller = scenario.redpanda_cluster.wait_leader("controller", namespace="redpanda", timeout_s=10)
        logger.debug(f"controller's leader: {controller.ip}")
        
        replicas_info = scenario.redpanda_cluster.wait_replicas(scenario.topic, partition=scenario.partition, timeout_s=10)
        if len(replicas_info.replicas)==1:
            raise Exception(f"topic {scenario.topic} has replication factor of 1: can't find a follower")

        self.follower = None
        for replica in replicas_info.replicas:
            if replica == replicas_info.leader:
                continue
            if self.follower == None:
                self.follower = replica
            if replica != controller:
                self.follower = replica
        
        for node in scenario.redpanda_cluster.nodes:
            if node == self.follower:
                continue
            self.rest.append(node.ip)
        
        logger.debug(f"isolating {scenario.topic}'s follower: {self.follower.ip}")

        ssh("ubuntu@"+self.follower.ip, "/mnt/vectorized/control/network.isolate.sh", *self.rest)
    
    def heal(self, scenario):
        ssh("ubuntu@"+self.follower.ip, "/mnt/vectorized/control/network.heal.sh", *self.rest)