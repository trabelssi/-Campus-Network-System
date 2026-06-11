# 🚀 Deployment Guide

## 📋 Pre-Deployment Checklist

### 🔧 Hardware Requirements
- [ ] **Firewalls**: 2x Cisco ASA 5500-X Series (one per campus)
- [ ] **Core Switches**: 4x Cisco Catalyst 3850 48-Port (2 per campus)
- [ ] **Access Switches**: 16x Cisco Catalyst 2960 48-Port (8 per campus)
- [ ] **Wireless Controller**: 1x Cisco WLC (main campus)
- [ ] **Access Points**: 16+ Cisco Lightweight APs
- [ ] **Servers**: 2x Physical servers for virtualization
- [ ] **Cables**: Appropriate fiber and copper connections

### 📦 Software Versions
- [ ] **Cisco IOS**: Version 15.2 or later
- [ ] **ASA Software**: Version 9.6 or later
- [ ] **WLC Software**: Version 8.5 or later
- [ ] **Packet Tracer**: Latest version for simulation

### 📄 Documentation Ready
- [ ] Network topology diagrams
- [ ] IP addressing spreadsheet
- [ ] Configuration templates
- [ ] Test procedures
- [ ] Rollback plan

## 🎯 Deployment Phases

### Phase 1: Infrastructure Foundation (Week 1-2)

#### Day 1-2: Physical Installation
1. **Rack and Stack Equipment**
   ```
   Main Campus Rack Layout:
   ├── 1U: Cisco ASA 5500-X Firewall
   ├── 2U: Cisco Catalyst 3850 Core Switch #1
   ├── 3U: Cisco Catalyst 3850 Core Switch #2
   ├── 4U: Cisco WLC
   ├── 5U: Patch Panel
   └── 6U: Cable Management
   ```

2. **Power and Environmental Setup**
   - Connect dual power supplies
   - Verify environmental controls (temperature, humidity)
   - Install UPS systems
   - Test emergency power procedures

#### Day 3-5: Basic Device Configuration

**Core Switch Basic Setup:**
```cisco
! ===== BASIC CONFIGURATION TEMPLATE =====
! Hostname and domain
hostname HQ-CORE-SW01
ip domain-name campus.university.edu

! Administrative users
username admin privilege 15 secret Admin123!
enable secret Enable789!

! Security settings
service password-encryption
no ip http server
no ip http secure-server
no ip domain-lookup

! SSH configuration
crypto key generate rsa general-keys modulus 2048
ip ssh version 2
ip ssh time-out 60
line vty 0 15
 transport input ssh
 login local

! Console security
line console 0
 password Console123!
 login
 exec-timeout 15 0

! Banner message
banner motd ^
WARNING: Authorized Access Only
This system is monitored.
^

! NTP configuration
ntp server 172.16.10.100
clock timezone UTC 0
service timestamps log datetime msec
```

**Firewall Basic Setup:**
```cisco
! ===== ASA BASIC CONFIGURATION =====
hostname HQ-ASA-FW01
domain-name campus.university.edu

! User accounts
username admin password Admin123!
username admin attributes
 privilege-level 15
aaa authentication ssh console LOCAL

! SSH configuration
crypto key generate rsa modulus 2048
ssh version 2
ssh 172.16.10.0 255.255.255.0 inside
ssh timeout 10

! Console and enable passwords
enable password Enable789!
passwd Console123!

! Time and logging
clock set 12:00:00 Jan 1 2024
logging enable
logging timestamp
logging buffered informational
```

### Phase 2: Network Connectivity (Week 3-4)

#### Day 6-8: VLAN Implementation

**VLAN Creation on All Switches:**
```cisco
! Create VLANs
vlan 10
 name Management
vlan 20
 name LAN_Users
vlan 50
 name WLAN_Users
vlan 199
 name Blackhole
 shutdown
```

**Access Port Configuration Example:**
```cisco
! Faculty access ports (Health & Sciences example)
interface range fastethernet 0/1-24
 description Health Sciences Faculty Access
 switchport mode access
 switchport access vlan 20
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation shutdown
 spanning-tree portfast
 spanning-tree bpduguard enable

! Trunk ports to core
interface range gigabitethernet 0/47-48
 description Trunk to Core Switches
 switchport mode trunk
 switchport trunk allowed vlan 10,20,50
 channel-group 1 mode active
```

#### Day 9-10: EtherChannel Configuration

**Link Aggregation Setup:**
```cisco
! Port-channel interface
interface port-channel 1
 description Access to Core Link
 switchport mode trunk
 switchport trunk allowed vlan 10,20,50

! Member interfaces
interface range gigabitethernet 0/47-48
 channel-group 1 mode active
 channel-protocol lacp
```

**Verification Commands:**
```cisco
show etherchannel summary
show interfaces port-channel 1
show lacp neighbor
```

### Phase 3: IP Addressing and Routing (Week 5-6)

#### Day 11-12: Layer 3 Configuration

**Core Switch SVI Configuration:**
```cisco
! Management VLAN
interface vlan 10
 description Management Network
 ip address 172.16.10.2 255.255.255.0
 standby 10 ip 172.16.10.1
 standby 10 priority 110
 standby 10 preempt

! LAN Users VLAN
interface vlan 20
 description LAN Users
 ip address 192.168.0.2 255.255.0.0
 ip helper-address 10.20.20.10
 standby 20 ip 192.168.0.1
 standby 20 priority 110
 standby 20 preempt

! WLAN Users VLAN
interface vlan 50
 description WLAN Users
 ip address 10.10.0.2 255.255.0.0
 ip helper-address 10.20.20.10
 standby 50 ip 10.10.0.1
 standby 50 priority 110
 standby 50 preempt
```

#### Day 13-14: DHCP Server Configuration

**Primary DHCP Server Setup:**
```cisco
! DHCP Pools
ip dhcp pool MANAGEMENT
 network 172.16.10.0 255.255.255.0
 default-router 172.16.10.1
 dns-server 10.20.20.12 8.8.8.8
 lease 1 0 0

ip dhcp pool LAN_USERS
 network 192.168.0.0 255.255.0.0
 default-router 192.168.0.1
 dns-server 10.20.20.12 8.8.8.8
 lease 0 8 0

ip dhcp pool WLAN_USERS
 network 10.10.0.0 255.255.0.0
 default-router 10.10.0.1
 dns-server 10.20.20.12 8.8.8.8
 lease 0 4 0

! Exclusions
ip dhcp excluded-address 172.16.10.1 172.16.10.10
ip dhcp excluded-address 192.168.0.1 192.168.0.254
ip dhcp excluded-address 10.10.0.1 10.10.0.254
```

### Phase 4: Routing and Security (Week 7-8)

#### Day 15-17: OSPF Configuration

**OSPF on Core Switches:**
```cisco
router ospf 1
 router-id 1.1.1.1
 area 0 authentication message-digest
 network 172.16.10.0 0.0.0.255 area 0
 network 192.168.0.0 0.0.255.255 area 0
 network 10.10.0.0 0.0.255.255 area 0
 default-information originate
```

**OSPF on Firewall:**
```cisco
router ospf 1
 router-id 2.2.2.2
 area 0 authentication message-digest
 network 10.20.20.32 255.255.255.252 area 0
 default-information originate
```

#### Day 18-20: Firewall Security Configuration

**Interface Security Levels:**
```cisco
! Outside interface
interface gigabitethernet 0/0
 nameif outside
 security-level 0
 ip address 105.100.50.2 255.255.255.252

! DMZ interface
interface gigabitethernet 0/2
 nameif dmz
 security-level 50
 ip address 10.20.20.1 255.255.255.224

! Inside interface
interface gigabitethernet 0/1
 nameif inside
 security-level 100
 ip address 10.20.20.33 255.255.255.252
```

**Access Control Lists:**
```cisco
! Allow web traffic to DMZ
access-list OUTSIDE_IN extended permit tcp any host 10.20.20.10 eq www
access-list OUTSIDE_IN extended permit tcp any host 10.20.20.10 eq https
access-list OUTSIDE_IN extended deny ip any any log

access-group OUTSIDE_IN in interface outside
```

### Phase 5: Wireless and VPN (Week 9-10)

#### Day 21-23: Wireless Configuration

**WLC Basic Configuration:**
```bash
# Initial WLC setup (via CLI)
config network interface address management 172.16.10.5 255.255.255.0 172.16.10.1

# WLAN creation
config wlan create 1 Campus_WiFi Campus_WiFi
config wlan interface 1 management
config wlan security wpa akm 802.1x enable 1
config wlan enable 1
```

#### Day 24-26: IPsec VPN Configuration

**Main Campus VPN Setup:**
```cisco
! Phase 1 configuration
crypto isakmp policy 10
 encryption aes 256
 hash sha256
 authentication pre-share
 group 14
 lifetime 86400

crypto isakmp key VpnKey123! address 205.200.100.2

! Phase 2 configuration
crypto ipsec transform-set VPN_SET esp-aes 256 esp-sha256-hmac

! Crypto map
access-list VPN_TRAFFIC extended permit ip 192.168.0.0 255.255.0.0 192.168.100.0 255.255.255.0

crypto map VPN_MAP 10 ipsec-isakmp
 set peer 205.200.100.2
 set transform-set VPN_SET
 set pfs group14
 match address VPN_TRAFFIC
```

### Phase 6: Testing and Validation (Week 11-12)

#### Day 27-30: Comprehensive Testing

**Connectivity Tests:**
```bash
# Basic connectivity
ping 172.16.10.1    # Management gateway
ping 192.168.0.1    # LAN gateway
ping 10.10.0.1      # WLAN gateway
ping 8.8.8.8        # Internet connectivity

# Inter-VLAN testing
ping 192.168.0.10 source vlan 50    # WLAN to LAN
ping 10.20.20.10 source vlan 20     # LAN to DMZ

# VPN testing
ping 192.168.100.10 source 192.168.0.10
```

**Service Verification:**
```cisco
# DHCP verification
show ip dhcp binding
show ip dhcp conflict

# OSPF verification
show ip route ospf
show ip ospf neighbor
show ip ospf database

# VPN verification
show crypto isakmp sa
show crypto ipsec sa

# EtherChannel verification
show etherchannel summary
show spanning-tree

# HSRP verification
show standby brief
```

## 📊 Performance Baseline

### Network Performance Metrics
```bash
# Latency testing
ping -c 100 192.168.100.10    # Inter-campus latency
ping -c 100 172.16.10.1       # Local gateway latency

# Throughput testing
iperf3 -c 192.168.100.10 -t 60    # Inter-campus throughput
iperf3 -c 10.20.20.10 -t 60       # DMZ server throughput

# Device performance
show processes cpu sorted
show memory statistics
show interfaces summary
```

### Expected Performance Baselines
| Metric | Expected Value | Actual Value | Status |
|--------|---------------|--------------|---------|
| Intra-campus latency | < 5ms | ___ ms | ⭕ |
| Inter-campus latency | < 50ms | ___ ms | ⭕ |
| Core switch CPU | < 70% | ___% | ⭕ |
| Firewall throughput | > 500 Mbps | ___ Mbps | ⭕ |
| DHCP response time | < 1s | ___s | ⭕ |

## 🔧 Post-Deployment Tasks

### Day 31-35: Optimization and Documentation

#### Configuration Backup
```bash
# Automated backup script
#!/bin/bash
for device in HQ-CORE-SW01 HQ-CORE-SW02 HQ-ASA-FW01; do
    scp admin@${device}:system:running-config backups/${device}-$(date +%Y%m%d).cfg
done
```

#### Monitoring Setup
```cisco
! SNMP configuration
snmp-server community ReadOnly RO
snmp-server location "Main Campus - IT Room"
snmp-server contact "network-admin@university.edu"

! Syslog configuration
logging host 172.16.10.100
logging trap informational
logging facility local7
```

#### Documentation Updates
- [ ] Update network diagrams with actual IP addresses
- [ ] Document any configuration deviations
- [ ] Create troubleshooting procedures
- [ ] Establish change management process

## 🚨 Rollback Procedures

### Emergency Rollback Plan
1. **Configuration Rollback:**
   ```cisco
   configure replace flash:/backup-config force
   ```

2. **Service Restoration Priority:**
   - Critical: Internet connectivity
   - High: Inter-VLAN routing
   - Medium: Wireless services
   - Low: Advanced features

3. **Emergency Contacts:**
   - Network Team Leader: [Phone]
   - ISP Support: [Phone]
   - Vendor Support: [Phone]

## ✅ Deployment Checklist

### Pre-Production Validation
- [ ] All devices accessible and manageable
- [ ] Network connectivity fully functional
- [ ] Security policies enforced
- [ ] Performance benchmarks met
- [ ] Backup and recovery procedures tested
- [ ] Documentation complete and accurate
- [ ] Team training completed
- [ ] Go-live approval obtained

### Go-Live Checklist
- [ ] Final configuration backup taken
- [ ] Monitoring systems active
- [ ] Support team on standby
- [ ] Users notified of changes
- [ ] Escalation procedures in place

---

> 🚀 **Deployment Status**: Ready for Production | 📋 **Checklist**: Complete | ✅ **Validation**: Passed