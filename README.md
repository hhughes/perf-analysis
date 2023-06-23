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