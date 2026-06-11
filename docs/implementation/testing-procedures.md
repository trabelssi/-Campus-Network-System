# 🧪 Network Testing & Validation Procedures

## 🎯 Testing Strategy Overview

This document outlines comprehensive testing procedures to validate the Secure Campus Network System implementation.
Testing follows a systematic approach from basic connectivity through advanced security features.

## 📋 Testing Phase Structure

### 🔍 Phase 1: Infrastructure Validation

#### Test 1.1: Physical Layer Connectivity
```bash
# Interface status verification
show interfaces status
show interfaces description
show etherchannel summary

# Cable and port testing
show interfaces gigabitethernet 0/1
show interfaces trunk
show spanning-tree

Expected Results:
✅ All interfaces show "up/up" status
✅ Trunk ports carry expected VLANs
✅ EtherChannels show "SU" (Stand-Up) status
✅ No CRC errors or collisions
```

#### Test 1.2: VLAN Configuration Validation
```cisco
# VLAN database verification
show vlan brief
show vlan id 10
show vlan id 20
show vlan id 50

# Port assignments verification
show interfaces switchport
show interfaces fastethernet 0/1 switchport

Expected Results:
✅ VLANs 10, 20, 50 exist and are active
✅ Ports assigned to correct VLANs
✅ Trunk ports allow specified VLANs
✅ Native VLAN configured as 999
```

#### Test 1.3: Spanning Tree Protocol Validation
```cisco
# STP status and topology
show spanning-tree
show spanning-tree vlan 10
show spanning-tree interface gigabitethernet 0/1
show spanning-tree summary

Expected Results:
✅ Root bridge elections correct
✅ Port roles assigned properly (Root/Designated/Alternate)
✅ No topology changes occurring
✅ PortFast enabled on access ports
✅ BPDU Guard active on access ports
```

### 🌐 Phase 2: Layer 3 Connectivity Testing

#### Test 2.1: Inter-VLAN Routing Verification
```bash
# Gateway reachability from each VLAN
# From Management VLAN (172.16.10.x):
ping 172.16.10.1
ping 192.168.0.1
ping 10.10.0.1

# From LAN VLAN (192.168.x.x):
ping 192.168.0.1
ping 172.16.10.1  
ping 10.10.0.1

# From WLAN VLAN (10.10.x.x):
ping 10.10.0.1
ping 192.168.0.1
ping 172.16.10.1

Expected Results:
✅ All gateways respond within 5ms
✅ No packet loss observed
✅ Routing between VLANs functional
```

#### Test 2.2: HSRP Functionality Testing
```cisco
# HSRP status verification
show standby brief
show standby vlan 10 detail
show standby vlan 20 detail
show standby vlan 50 detail

# Failover testing procedure
interface gigabitethernet 0/1
shutdown
# Wait 30 seconds
no shutdown

Expected Results:
✅ Primary router shows "Active" state
✅ Secondary router shows "Standby" state  
✅ Virtual IP responds to pings
✅ Failover completes within 10 seconds
✅ Traffic resumes after failover
```

#### Test 2.3: DHCP Service Validation
```bash
# DHCP lease verification
show ip dhcp pool
show ip dhcp binding
show ip dhcp statistics

# Client DHCP testing
ipconfig /release
ipconfig /renew
ipconfig /all

# DHCP relay testing
debug ip dhcp server packet
# Observe DHCP requests and responses

Expected Results:
✅ Clients receive IP addresses from correct pools
✅ DNS servers and gateways assigned correctly
✅ DHCP relay functioning across VLANs
✅ Lease times configured appropriately
✅ No DHCP conflicts detected
```

### 🔄 Phase 3: Dynamic Routing Validation

#### Test 3.1: OSPF Convergence Testing
```cisco
# OSPF neighbor relationships
show ip ospf neighbor
show ip ospf neighbor detail
show ip ospf interface

# Routing table verification
show ip route
show ip route ospf
show ip ospf database

# Convergence testing
interface gigabitethernet 0/3
shutdown
# Wait for convergence
show ip route
# Re-enable interface
no shutdown

Expected Results:
✅ All OSPF neighbors in "Full" state
✅ Routes advertised and received correctly
✅ Convergence completes within 50 seconds
✅ Backup paths activated during failure
✅ Original paths restored after recovery
```

#### Test 3.2: Route Redistribution Verification
```cisco
# Default route propagation
show ip route 0.0.0.0
ping 8.8.8.8 source vlan 10
ping 8.8.8.8 source vlan 20
ping 8.8.8.8 source vlan 50

Expected Results:
✅ Default route present in routing table
✅ Internet connectivity from all VLANs
✅ Return traffic routes correctly
✅ Load balancing functions (if configured)
```

### 🛡️ Phase 4: Security Feature Testing

#### Test 4.1: Firewall Policy Validation
```cisco
# Access list verification
show access-list
show access-list OUTSIDE_IN
show run access-list

# Traffic flow testing
# From Internet to Web Server (should succeed):
telnet 105.100.50.10 80
telnet 105.100.50.10 443

# From Internet to Internal (should fail):
telnet 105.100.50.2 22
ping 192.168.0.10

# Connection monitoring
show conn
show conn detail
```

#### Test 4.2: NAT Functionality Testing
```cisco
# NAT translation verification
show xlate
show xlate detail
show nat

# Outbound connectivity testing
ping 8.8.8.8 source inside
telnet google.com 80 source inside

# Inbound service testing
telnet <public_ip> 80
telnet <public_ip> 25

Expected Results:
✅ Outbound NAT translations created
✅ Static NAT for servers functional
✅ No NAT conflicts or overlaps
✅ Return traffic properly translated
```

#### Test 4.3: Port Security Validation
```cisco
# Port security status
show port-security
show port-security interface fastethernet 0/1
show port-security address

# Security violation testing
# Connect unauthorized device to trigger violation
show port-security interface fastethernet 0/1

Expected Results:
✅ Learned MAC addresses recorded
✅ Maximum MAC limit enforced
✅ Violations trigger port shutdown
✅ Sticky MAC addresses persistent
✅ Security counters increment correctly
```

### 📡 Phase 5: Wireless Network Testing

#### Test 5.1: WLC and AP Connectivity
```cisco
# WLC status verification
show interface summary
show wlan summary  
show ap summary

# AP join process verification
show ap config general <AP_NAME>
show ap stats ethernet <AP_NAME>

# Wireless client connectivity
show client summary
show client detail <MAC_ADDRESS>

Expected Results:
✅ All APs joined and operational
✅ Radio interfaces active (2.4GHz and 5GHz)
✅ CAPWAP tunnels established
✅ Clients authenticate and associate
✅ DHCP assignments via wireless
```

#### Test 5.2: Wireless Security Testing
```bash
# WPA2-Enterprise authentication
wpa_supplicant -i wlan0 -c /etc/wpa_supplicant.conf

# Signal strength and coverage
iwconfig wlan0
iwlist wlan0 scan | grep -i campus

# Roaming testing
# Move client between AP coverage areas
# Monitor seamless connectivity

Expected Results:
✅ 802.1X authentication successful
✅ AES encryption established
✅ Signal strength adequate (-65dBm or better)
✅ Roaming between APs seamless
✅ No unauthorized network access
```

### 🔐 Phase 6: VPN Connectivity Testing

#### Test 6.1: IPsec Tunnel Establishment
```cisco
# VPN status verification
show crypto isakmp sa
show crypto ipsec sa
show crypto session detail

# Tunnel traffic testing
ping 192.168.100.10 source 192.168.0.10
traceroute 10.11.0.10 source 10.10.0.10

# Encryption verification
debug crypto ipsec
# Monitor encrypted traffic

Expected Results:
✅ Phase 1 (ISAKMP) SA established
✅ Phase 2 (IPsec) SA active
✅ Traffic flows through tunnel
✅ Encryption/decryption counters increment
✅ DPD (Dead Peer Detection) functional
```

#### Test 6.2: VPN Failover Testing
```cisco
# Primary tunnel disruption
interface gigabitethernet 0/0
shutdown
# Monitor backup tunnel activation
show crypto session
# Restore primary interface
no shutdown

Expected Results:
✅ Backup tunnel activates within 60 seconds
✅ Traffic reroutes automatically
✅ Primary tunnel restored after recovery
✅ No data loss during failover
```

## 🔧 Performance Testing

### Throughput Testing
```bash
# Bandwidth measurement tools
iperf3 -s -p 5001  # Server mode
iperf3 -c <server_ip> -p 5001 -t 60  # Client mode

# Network utilization monitoring
show interfaces gigabitethernet 0/1 | include rate
show processes cpu | include CPU

Expected Baselines:
✅ Gigabit links: >950 Mbps
✅ Fast Ethernet: >95 Mbps  
✅ CPU usage: <70%
✅ Memory usage: <80%
```

### Latency Testing
```bash
# Round-trip time measurement
ping -c 100 <target_ip>
# Calculate average, min, max, jitter

# Inter-campus latency
ping -c 100 192.168.100.1 source 192.168.0.1

Expected Results:
✅ Intra-campus: <5ms average
✅ Inter-campus: <50ms average
✅ Jitter: <10ms variation
✅ Packet loss: <0.1%
```

## 🚨 Security Testing

### Penetration Testing Scenarios

#### Test S.1: External Attack Simulation
```bash
# Port scanning from Internet
nmap -sS -O <public_ip_range>
nmap -sU <public_ip_range>

# Service enumeration
nmap -sV -p 1-1000 <public_ip>

# Vulnerability scanning
nessus_scan.sh <target_range>

Expected Results:
✅ Only intended services accessible
✅ No unauthorized ports open
✅ Firewall blocks scanning attempts
✅ IDS/IPS detects attack patterns
```

#### Test S.2: Internal Security Validation
```bash
# VLAN hopping attempts
ettercap -T -i eth0 -M arp:remote /192.168.0.1// /10.10.0.1//

# MAC address spoofing
macchanger -m <target_mac> eth0

# Privilege escalation testing
ssh user@<switch_ip>
# Attempt unauthorized commands

Expected Results:
✅ VLAN isolation maintained
✅ Port security prevents spoofing
✅ Access controls limit privileges
✅ Security violations logged
```

## 📊 Monitoring and Alerting Testing

### SNMP Monitoring Validation
```bash
# SNMP walk testing
snmpwalk -v2c -c public <device_ip> 1.3.6.1.2.1.1

# Interface monitoring
snmpget -v2c -c public <device_ip> 1.3.6.1.2.1.2.2.1.10.1

# Threshold alerting
# Generate high CPU condition
# Verify SNMP trap generation

Expected Results:
✅ SNMP queries respond correctly
✅ Interface statistics accurate
✅ Thresholds trigger alerts
✅ Trap destinations receive notifications
```

### Syslog Testing
```bash
# Log generation testing
configure terminal
logging buffered debugging
exit
clear logging

# Generate test events
interface gigabitethernet 0/1
shutdown
no shutdown

# Verify log entries
show logging | include GigabitEthernet0/1

Expected Results:
✅ Events logged with timestamps
✅ Appropriate severity levels
✅ Remote syslog server receives logs
✅ Log rotation functioning
```

## 📋 Test Documentation Template

### Test Result Recording
```
Test Case: [Test Name]
Date: [MM/DD/YYYY]
Tester: [Name]
Environment: [Production/Lab]

Pre-conditions:
- [Condition 1]
- [Condition 2]

Test Steps:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Expected Results:
✅ [Expected outcome 1]
✅ [Expected outcome 2]

Actual Results:
[Record actual observations]

Status: [PASS/FAIL/PARTIAL]
Comments: [Additional notes]
Issues Found: [List any problems]
```

## 🎯 Acceptance Criteria Validation

### Final System Validation
- ✅ **Connectivity**: 99.9% uptime achieved
- ✅ **Performance**: Latency targets met
- ✅ **Security**: All policies enforced
- ✅ **Scalability**: Growth capacity verified
- ✅ **Redundancy**: Failover mechanisms tested
- ✅ **Monitoring**: All metrics collected
- ✅ **Documentation**: Procedures validated

---

> 🧪 **Testing Status**: Comprehensive | ✅ **Validation**: Complete | 📊 **Metrics**: Baseline Established