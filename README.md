# Java-driver perf log analysis tool

Lists top messages by level from java-driver fallout test logs.

### Features
- [x] Process java-driver fallout logs, consolidate multi-line messages
- [x] Print top N (default=10) messages per level
- [x] Read from file or std-in
- [x] Substitutions for variable fields to improve matching (IP addresses, jar versions, line numbers etc)
- [x] Compare top messages between two files

### Todo / wishlist
- [ ] Use fallout API to download result/run tests automatically
- [ ] Compare more than two files
- [ ] Show progress during processing

## Usage
(stacktraces truncated for readability)

Show top messages from perf run:
```
% python java_driver.py /path/to/logfile --types=logback --sub=ip,uuid,hex,java_line,jar,inflight              
**** logback messages ****
--------------------------------------------------------------------------------
  INFO - total: 69712
  top messages:
   * 26345: [id: 0x$HEX, L:/$IP_ADDRESS - R:/$IP_ADDRESS] $INFLIGHT=?   , orphaned=0    , open=true, protocol version=V5
   * 15318: [id: 0x$HEX, L:/$IP_ADDRESS - R:/$IP_ADDRESS] $INFLIGHT=?    , orphaned=0    , open=true, protocol version=V5
   * 8006: Completed $HEX suite tests...
   * 2002: Host States for Session duration_test#0: 
   * 1045: [datacenter1:rack1:Optional[/$IP_ADDRESS]] version=4.0.10, state=DOWN, dist=LOCAL, totalInFlight=0    , orphaned=0    , openConnections=0, reconnecting=true. pool=$HEX, poolClosed=false
   * 1042: Query Plan: [Node(endPoint=/$IP_ADDRESS, hostId=$UUID, hashCode=$HEX), Node(endPoint=/$IP_ADDRESS, hostId=$UUID, hashCode=$HEX)]
   * 957: Query Plan: [Node(endPoint=/$IP_ADDRESS, hostId=$UUID, hashCode=$HEX), Node(endPoint=/$IP_ADDRESS, hostId=$UUID, hashCode=$HEX), Node(endPoint=/$IP_ADDRESS, hostId=$UUID, hashCode=$HEX)]
   * 26: [datacenter1:rack1:Optional[/$IP_ADDRESS]] version=4.0.10, state=UP, dist=LOCAL, totalInFlight=315  , orphaned=0    , openConnections=8, reconnecting=false. pool=$HEX, poolClosed=false
   * 25: [datacenter1:rack1:Optional[/$IP_ADDRESS]] version=4.0.10, state=UP, dist=LOCAL, totalInFlight=313  , orphaned=0    , openConnections=8, reconnecting=false. pool=$HEX, poolClosed=false
   * 24: [id: 0x$HEX, L:/$IP_ADDRESS - R:/$IP_ADDRESS] $INFLIGHT=?  , orphaned=0    , open=true, protocol version=V5
--------------------------------------------------------------------------------
  WARN - total: 13666
  top messages:
   * 11664: [s1|/$IP_ADDRESS]  Error while opening new channel
com.datastax.oss.driver.api.core.connection.ConnectionInitException: [s1|connecting...] Protocol initialization request, step 1 (STARTUP {CQL_VERSION=3.0.0, DRIVER_NAME=DataStax Java driver for Apache Cassandra(R), DRIVER_VERSION=4.16.1-SNAPSHOT, CLIENT_ID=$UUID}): failed to send request (io.netty.channel.StacklessClosedChannelException)
	at com.datastax.oss.driver.internal.core.channel.ProtocolInitHandler$InitRequest.fail(ProtocolInitHandler.java:$LINE) ~[$JAR:?]
<snip>
	at java.lang.Thread.run(Thread.java:$LINE) ~[na:1.8.0_362]
	Suppressed: io.netty.channel.AbstractChannel$AnnotatedConnectException: Connection refused: /$IP_ADDRESS
	Caused by: java.net.ConnectException: Connection refused
		at sun.nio.ch.SocketChannelImpl.checkConnect(Native Method)
<snip>
		at java.lang.Thread.run(Thread.java:$LINE)
Caused by: io.netty.channel.StacklessClosedChannelException: null
	at io.netty.channel.AbstractChannel$AbstractUnsafe.flush0()(Unknown Source) ~[$JAR:?]
   * 1999: Control connection is open:
   * 3: Control connection is closed:
--------------------------------------------------------------------------------
  ERROR - total: 3
  top messages:
   * 2: Exception encountered while logging session state.
java.lang.NullPointerException: null
   * 1: Exception encountered while logging session state.
java.lang.NullPointerException: null
	at sun.reflect.UnsafeFieldAccessorImpl.ensureObj(UnsafeFieldAccessorImpl.java:$LINE) ~[na:1.8.0_362]
<snip>
	at java.lang.Thread.run(Thread.java:$LINE) [na:1.8.0_362]
--------------------------------------------------------------------------------
```

Compare messages from two logs:
```
% python java_driver.py /path/to/first/logfile --types=logback --levels=WARN,ERROR --sub=ip,uuid,hex,java_line,jar,inflight --compare-to=/path/to/second/logfile
**** logback messages ****
--------------------------------------------------------------------------------
  WARN - total: 40110 (baseline: 40048)
  top messages:
   * 34328 (baseline: 34272): [s1|/$IP_ADDRESS]  Error while opening new channel
com.datastax.oss.driver.api.core.connection.ConnectionInitException: [s1|connecting...] Protocol initialization request, step 1 (STARTUP {CQL_VERSION=3.0.0, DRIVER_NAME=DataStax Java driver for Apache Cassandra(R), DRIVER_VERSION=4.16.1-SNAPSHOT, CLIENT_ID=$UUID}): failed to send request (io.netty.channel.StacklessClosedChannelException)
	at com.datastax.oss.driver.internal.core.channel.ProtocolInitHandler$InitRequest.fail(ProtocolInitHandler.java:$LINE) ~[$JAR:?]
<snip>
		at java.lang.Thread.run(Thread.java:$LINE)
Caused by: io.netty.channel.StacklessClosedChannelException: null
	at io.netty.channel.AbstractChannel$AbstractUnsafe.flush0()(Unknown Source) ~[$JAR:?]
   * 5739 (baseline: 5733): Control connection is open:
   * 38 (baseline: 31): Cassandra timeout during read query at consistency ALL (3 responses were required but only 2 replica responded). In case this was generated during read repair, the consistency level is not representative of the actual consistency.
   * 5 (baseline: 12): Control connection is closed:
--------------------------------------------------------------------------------
  ERROR - total: 1546 (baseline: 1016)
  top messages:
   * 979 (baseline: 999): Unexpected exception while executing statement, aborting execution.
com.datastax.oss.driver.api.core.DriverTimeoutException: Query timed out after PT3S
	at com.datastax.oss.driver.internal.core.cql.CqlRequestHandler.lambda$scheduleTimeout$1(CqlRequestHandler.java:$LINE) [$JAR:?]
<snip>
	at java.lang.Thread.run(Thread.java:$LINE) ~[na:1.8.0_362]
   * 538 (baseline: 0): Unexpected exception while executing statement, aborting execution.
com.datastax.oss.driver.api.core.servererrors.UnavailableException: Not enough replicas available for query at consistency LOCAL_QUORUM (2 required but only 1 alive)
   * 9 (baseline: 0): Exception encountered.
java.util.concurrent.CompletionException: com.datastax.oss.driver.api.core.servererrors.UnavailableException: Not enough replicas available for query at consistency LOCAL_QUORUM (2 required but only 1 alive)
	at java.util.concurrent.CompletableFuture.encodeThrowable(CompletableFuture.java:$LINE) ~[na:1.8.0_362]
<snip>
Caused by: com.datastax.oss.driver.api.core.servererrors.UnavailableException: Not enough replicas available for query at consistency LOCAL_QUORUM (2 required but only 1 alive)
<snip>
--------------------------------------------------------------------------------
```

# Tracing node-list and control connections

Groups logs by hostId/broadcast-address to help debug issues with running out of available connections (NoHostsAvailable exception)

### Usage

Here is an example output showing the interesting lifecycle events for one host, the rest of the output has been truncated for brevity.

```
cat application.log | python ./trace_connections.py

host id: 01323ae9-e801-424b-a1e9-7c9357fb109d (REDACTED_IP:REDACTED_PORT)
---------------------------------------------
  10:45:46.048 [s0-admin-0] c.d.o.d.i.c.metadata.MetadataManager - [s0] Adding initial contact points [Node(endPoint=REDACTED_HOST:REDACTED_PORT:3ad25c3a-4b96-4777-9c6d-33739d355a4e, hostId=null, hashCode=1bb54e45, dc=null), Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=null, hashCode=356a3911, dc=null), Node(endPoint=REDACTED_HOST:REDACTED_PORT:228a5703-3858-449f-ba98-d72d2b1472f9, hostId=null, hashCode=2b23df63, dc=null)]
  10:45:46.051 [s0-admin-1] c.d.o.d.i.c.c.ControlConnection - [s0] Control connection candidate nodes: [Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=null, hashCode=356a3911, dc=null), Node(endPoint=REDACTED_HOST:REDACTED_PORT:228a5703-3858-449f-ba98-d72d2b1472f9, hostId=null, hashCode=2b23df63, dc=null), Node(endPoint=REDACTED_HOST:REDACTED_PORT:3ad25c3a-4b96-4777-9c6d-33739d355a4e, hostId=null, hashCode=1bb54e45, dc=null)]
  10:45:46.052 [s0-admin-1] c.d.o.d.i.c.c.ControlConnection - [s0] Trying to establish a connection to Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=null, hashCode=356a3911, dc=null)
  10:45:47.540 [s0-admin-1] c.d.o.d.i.c.c.ControlConnection - [s0] New channel opened [id: 0xdf0fd3ed, L:/REDACTED_IP:REDACTED_PORT - R:REDACTED_HOST/REDACTED_IP:REDACTED_PORT] to Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=null, hashCode=356a3911, dc=null)
  10:45:47.543 [s0-admin-1] c.d.o.d.i.c.m.NodeStateManager - [s0] Processing ChannelEvent(OPENED, Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=null, hashCode=356a3911, dc=null))
  10:45:47.544 [s0-admin-1] c.d.o.d.i.c.m.NodeStateManager - [s0] Transitioning Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=null, hashCode=356a3911, dc=null) UNKNOWN=>UP (because a new connection was opened to it)
  10:45:47.726 [s0-io-3] c.d.o.d.i.c.m.DefaultTopologyMonitor - [s0] Full system-table node list: <SNIP>
  10:45:47.728 [s0-admin-0] c.d.o.d.i.c.m.InitialNodeListRefresh - [s0] Copying contact point Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=null, hashCode=356a3911, dc=null) with system-table address /REDACTED_IP:REDACTED_PORT
  10:45:48.098 [s0-admin-0] c.d.o.d.i.c.m.LoadBalancingPolicyWrapper - [s0] com.datastax.oss.driver.internal.core.loadbalancing.DefaultLoadBalancingPolicy@633fad99 suggested Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1) to LOCAL, checking what other policies said
  10:45:48.098 [s0-admin-0] c.d.o.d.i.c.m.LoadBalancingPolicyWrapper - [s0] Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1) was IGNORED, changing to LOCAL
  10:45:48.098 [s0-admin-0] c.d.o.d.i.c.l.BasicLoadBalancingPolicy - [s0|default] Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1) added to initial live set
  10:45:48.099 [s0-admin-0] c.d.o.d.i.c.l.BasicLoadBalancingPolicy - [s0|default] Current live nodes by dc: {us-east1: Node(endPoint=REDACTED_HOST:REDACTED_PORT:228a5703-3858-449f-ba98-d72d2b1472f9, hostId=228a5703-3858-449f-ba98-d72d2b1472f9, hashCode=2b23df63, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:3ad25c3a-4b96-4777-9c6d-33739d355a4e, hostId=3ad25c3a-4b96-4777-9c6d-33739d355a4e, hashCode=1bb54e45, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1)}
  10:45:48.105 [s0-admin-1] c.d.o.d.i.core.session.PoolManager - [s0] Creating a pool for Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1)
  10:45:48.105 [s0-admin-1] c.d.o.d.i.core.pool.ChannelPool - [s0|REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d] Trying to create 1 missing channels
  10:45:48.588 [s0-admin-1] c.d.o.d.i.core.pool.ChannelPool - [s0|REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d] New channel added [id: 0x783cdab9, L:/REDACTED_IP:REDACTED_PORT - R:REDACTED_HOST/REDACTED_IP:REDACTED_PORT]
  10:45:48.590 [s0-admin-1] c.d.o.d.i.c.m.NodeStateManager - [s0] Processing ChannelEvent(OPENED, Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1))
  10:45:48.592 [s0-admin-1] c.d.o.d.i.core.pool.ChannelPool - [s0|REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d] Reconnection attempt complete, 1/1 channels
  10:50:05.648 [s0-io-3] c.d.o.d.i.c.m.DefaultTopologyMonitor - [s0] Full system-table node list: <SNIP>
  10:50:06.345 [s0-admin-1] c.d.o.d.i.c.l.BasicLoadBalancingPolicy - [s0|default] Current live nodes by dc: {us-east1: Node(endPoint=REDACTED_HOST:REDACTED_PORT:228a5703-3858-449f-ba98-d72d2b1472f9, hostId=228a5703-3858-449f-ba98-d72d2b1472f9, hashCode=2b23df63, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:3ad25c3a-4b96-4777-9c6d-33739d355a4e, hostId=3ad25c3a-4b96-4777-9c6d-33739d355a4e, hashCode=1bb54e45, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:8d33fae4-66d0-4109-80ca-c4deff95fa69, hostId=8d33fae4-66d0-4109-80ca-c4deff95fa69, hashCode=3f4dad9e, dc=us-east1)}
  10:51:06.288 [s0-io-3] c.d.o.d.i.c.m.DefaultTopologyMonitor - [s0] Full system-table node list: <SNIP>
  10:51:07.032 [s0-admin-1] c.d.o.d.i.c.l.BasicLoadBalancingPolicy - [s0|default] Current live nodes by dc: {us-east1: Node(endPoint=REDACTED_HOST:REDACTED_PORT:228a5703-3858-449f-ba98-d72d2b1472f9, hostId=228a5703-3858-449f-ba98-d72d2b1472f9, hashCode=2b23df63, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:3ad25c3a-4b96-4777-9c6d-33739d355a4e, hostId=3ad25c3a-4b96-4777-9c6d-33739d355a4e, hashCode=1bb54e45, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:8d33fae4-66d0-4109-80ca-c4deff95fa69, hostId=8d33fae4-66d0-4109-80ca-c4deff95fa69, hashCode=3f4dad9e, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:e1d18ba9-ce92-4f08-87a6-a7ceb739e953, hostId=e1d18ba9-ce92-4f08-87a6-a7ceb739e953, hashCode=56ac2aea, dc=us-east1)}
  10:51:16.179 [s0-admin-0] c.d.o.d.i.c.l.BasicLoadBalancingPolicy - [s0|default] Current live nodes by dc: {us-east1: Node(endPoint=REDACTED_HOST:REDACTED_PORT:228a5703-3858-449f-ba98-d72d2b1472f9, hostId=228a5703-3858-449f-ba98-d72d2b1472f9, hashCode=2b23df63, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:8d33fae4-66d0-4109-80ca-c4deff95fa69, hostId=8d33fae4-66d0-4109-80ca-c4deff95fa69, hashCode=3f4dad9e, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:e1d18ba9-ce92-4f08-87a6-a7ceb739e953, hostId=e1d18ba9-ce92-4f08-87a6-a7ceb739e953, hashCode=56ac2aea, dc=us-east1)}
  10:51:22.060 [s0-io-3] c.d.o.d.i.c.m.DefaultTopologyMonitor - [s0] Full system-table node list: <SNIP>
  10:51:22.715 [s0-admin-1] c.d.o.d.i.c.l.BasicLoadBalancingPolicy - [s0|default] Current live nodes by dc: {us-east1: Node(endPoint=REDACTED_HOST:REDACTED_PORT:228a5703-3858-449f-ba98-d72d2b1472f9, hostId=228a5703-3858-449f-ba98-d72d2b1472f9, hashCode=2b23df63, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:8d33fae4-66d0-4109-80ca-c4deff95fa69, hostId=8d33fae4-66d0-4109-80ca-c4deff95fa69, hashCode=3f4dad9e, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:e1d18ba9-ce92-4f08-87a6-a7ceb739e953, hostId=e1d18ba9-ce92-4f08-87a6-a7ceb739e953, hashCode=56ac2aea, dc=us-east1), Node(endPoint=REDACTED_HOST:REDACTED_PORT:7a6a4a3b-3585-4747-bbc6-2240328b04d3, hostId=7a6a4a3b-3585-4747-bbc6-2240328b04d3, hashCode=441078e, dc=us-east1)}
  10:57:31.437 [s0-io-3] c.d.o.d.i.c.c.ControlConnection - [s0] Processing incoming event EVENT TOPOLOGY_CHANGE(REMOVED_NODE /REDACTED_IP:REDACTED_PORT)
  10:57:32.446 [s0-admin-1] c.d.o.d.i.c.m.NodeStateManager - [s0] Coalesced topology events: [TopologyEvent(SUGGEST_REMOVED, /REDACTED_IP:REDACTED_PORT)] => [TopologyEvent(SUGGEST_REMOVED, /REDACTED_IP:REDACTED_PORT)]
  10:57:32.446 [s0-admin-1] c.d.o.d.i.c.m.NodeStateManager - [s0] Processing TopologyEvent(SUGGEST_REMOVED, /REDACTED_IP:REDACTED_PORT)
  10:57:32.447 [s0-admin-0] c.d.o.d.i.c.m.RemoveNodeRefresh - [s0] Removing node Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1)
  10:57:32.449 [s0-admin-0] c.d.o.d.i.c.l.BasicLoadBalancingPolicy - [s0|default] Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1) was removed, removed from live set
  10:57:32.449 [s0-admin-1] c.d.o.d.i.c.c.ControlConnection - [s0] Control node Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1) with channel [id: 0xdf0fd3ed, L:/REDACTED_IP:REDACTED_PORT - R:REDACTED_HOST/REDACTED_IP:REDACTED_PORT] was removed or forced down, reconnecting to a different node
  10:57:32.496 [s0-admin-1] c.d.o.d.i.core.session.PoolManager - [s0] Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1) was removed, destroying pool
  10:57:32.497 [s0-admin-1] c.d.o.d.i.c.m.NodeStateManager - [s0] Processing ChannelEvent(CLOSED, Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1))
  10:57:32.991 [s0-admin-1] c.d.o.d.i.c.m.NodeStateManager - [s0] Processing ChannelEvent(CLOSED, Node(endPoint=REDACTED_HOST:REDACTED_PORT:01323ae9-e801-424b-a1e9-7c9357fb109d, hostId=01323ae9-e801-424b-a1e9-7c9357fb109d, hashCode=356a3911, dc=us-east1))
  
host id: 3ad25c3a-4b96-4777-9c6d-33739d355a4e (REDACTED_IP:REDACTED_PORT)
---------------------------------------------
<TRUNCATED>
```