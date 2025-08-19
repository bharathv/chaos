# Redpanda Chaos Engineering Framework

A comprehensive chaos engineering framework for testing Apache Kafka-compatible streaming platform Redpanda under various failure conditions. This framework systematically injects faults into Redpanda clusters while running real workloads to validate system resilience, data consistency, and recovery capabilities.

## Architecture

The chaos testing framework follows a modular architecture with three main components:

### Core Components

- **Fault Injection Engine** (`harness/chaos/faults/`) - Implements 20+ different fault types for network, process, and configuration disruption
- **Workload Orchestration** (`harness/chaos/workloads/`) - Manages Java-based client applications that generate realistic load patterns
- **Test Scenarios** (`harness/chaos/scenarios/`) - Coordinates fault injection with workload execution and validation
- **Consistency Validation** - Built-in checkers that verify data integrity and transactional guarantees after fault recovery

### Infrastructure Support

- **Docker Compose** - Local testing with containerized Redpanda clusters (3-6 nodes)
- **Terraform + Ansible** - AWS deployment for production-scale testing
- **Control Scripts** - Shell-based automation for cluster management and workload lifecycle

## Fault Types

The framework implements a comprehensive suite of fault injection capabilities:

### Network Isolation Faults
- **isolate_controller** - Partition the Raft controller leader from the cluster
- **isolate_leader/follower** - Network isolate partition leaders or followers for specific topics
- **isolate_tx_leader/follower** - Target transaction coordinator nodes specifically
- **isolate_all/tx_all** - Complete cluster isolation or transaction subsystem isolation
- **isolate_client_topic_leader** - Isolate clients from topic leaders while maintaining cluster connectivity

### Process Termination Faults
- **kill_leader/follower/all** - Terminate Redpanda processes on leader, follower, or all nodes
- **kill_tx_leader/follower** - Target transaction coordinator processes
- **kill_partition** - Kill processes hosting specific partition replicas
- **pause_leader/follower/all** - Suspend processes using SIGSTOP for temporary unavailability

### Cluster Reconfiguration Faults
- **reconfigure_313** - Change cluster from 3 to 1 to 3 nodes (membership changes)
- **reconfigure_11_kill/kill_11** - Single node cluster transitions with process kills
- **leadership_transfer** - Force leadership changes without node failures
- **decommission_leader** - Remove leader nodes from cluster membership
- **rolling_restart** - Systematic restart of all cluster nodes

### Advanced Fault Scenarios
- **hijack_tx_ids** - Transaction ID manipulation to test edge cases in transactional processing
- **recycle_all/storm** - Aggressive node replacement simulating infrastructure failures
- **trigger_kip_360** - Test specific Kafka Improvement Proposal behaviors
- **isolate_clients_kill_leader** - Combined client isolation and leadership disruption

### Fault Combinators
- **as_oneoff** - Execute multiple faults as a single event
- **repeat** - Repeatedly apply fault patterns over time

## Test Scenarios

The framework provides 5 primary test scenarios that orchestrate workloads with fault injection:

### Basic Consistency Testing
- **single_table_single_fault** - Tests basic read/write operations on a single topic with one fault injection per test run. Validates fundamental consistency guarantees.

### Transactional Consistency Testing  
- **tx_single_table_single_fault** - Focuses on transactional read/write patterns on a single topic, ensuring ACID properties are maintained during faults.

### Financial Transaction Simulation
- **tx_money_single_fault** - Implements a bank account transfer simulation with strict consistency requirements. Tests multiple accounts, transfer operations, and balance validation under fault conditions.

### Consumer Group Resilience
- **tx_subscribe_single_fault** - Tests transactional consumer group behavior, including consume-transform-produce patterns with exactly-once semantics.
- **rw_subscribe_single_fault** - Validates non-transactional consumer group rebalancing, partition assignment, and offset management during faults.

## Workloads

### Basic Data Operations

**reads-writes** - Implements concurrent read and write operations with configurable concurrency levels. Validates basic data consistency and availability during faults.

**list-offsets** - Tests offset management, seeking behavior, and metadata consistency. Critical for consumer applications that need reliable offset tracking.

### Transactional Workloads

**tx-single-reads-writes** - Single-topic transactional patterns with read-modify-write operations. Tests transaction isolation levels and consistency during coordinator failures.

**tx-money** - Multi-account money transfer simulation implementing:
- Account creation and balance tracking across multiple topics
- Atomic transfer operations between accounts
- Balance validation and audit trails
- Strict consistency verification after fault recovery

**tx-compact** - Tests transactional behavior with log compaction enabled, ensuring transactions work correctly with Kafka's log cleanup policies.

**tx-subscribe** - Implements transactional consume-transform-produce patterns:
- Exactly-once message processing
- Consumer group coordination with transactions
- Cross-topic transactional writes
- Offset committing within transaction boundaries

### Consumer Group Testing

**rw-subscribe** - Tests consumer group resilience including:
- Partition rebalancing during member failures
- Offset management and duplicate prevention
- Consumer lag monitoring and recovery
- Group coordinator failover scenarios

### Workload Architecture

Each workload consists of:

**Java Client Applications** - Located in `workloads/uber/src/main/java/io/vectorized/`, these implement the actual data operations using Kafka client libraries.

**Python Control Layer** - Located in `harness/chaos/workloads/`, provides:
- **Consistency Checkers** - Validate data integrity after fault injection
- **Statistics Collection** - Gather performance metrics and operation counts  
- **Log Analysis** - Parse client logs to detect errors and inconsistencies
- **Health Monitoring** - Track process liveness and client connectivity

**Control Scripts** - Shell scripts in `control/` directory manage workload lifecycle:
- Start/stop operations for each workload type
- Health checking and process monitoring
- Log collection and cleanup

## Test Configuration Structure

Tests are defined in JSON files under `suites/tests/` with the following structure:

- **Workload Configuration** - Specifies client concurrency, operation types, and duration
- **Fault Injection Parameters** - Defines when and how faults are applied
- **Consistency Validation Rules** - Configures post-test verification requirements
- **Cluster Topology** - Sets replication factors, partition counts, and node assignments

Test suites in `suites/` aggregate multiple related tests with retry policies and error handling configurations.

The framework provides comprehensive coverage of Redpanda's fault tolerance capabilities across network partitions, process failures, configuration changes, and transactional edge cases, ensuring production deployments can handle real-world failure scenarios with confidence.
