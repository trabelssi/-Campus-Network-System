# ⚙️ Network Implementation & Configuration Guide

## 🎯 Implementation Overview

This guide provides step-by-step configuration procedures for implementing the Secure Campus Network System.
Follow the phases sequentially to ensure proper network convergence and functionality.

## 📋 Implementation Phases

### 🔧 Phase 1: Infrastructure Foundation

#### Step 1: Network Design & Documentation
```
Deliverables:
├── Physical topology diagram
├── Logical network diagram  
├── IP addressing spreadsheet
├── VLAN assignment matrix
└── Device naming convention
```

#### Step 2: Basic Device Configuration

##### 2.1 Global Configuration Standards
```cisco
! Hostname Configuration
hostname HQ-CORE-SW01

! Domain and DNS
ip domain-name campus.university.edu  
ip name-server 10.20.20.12
ip name-server 8.8.8.8

! Disable unnecessary services
no ip http server
no ip http secure-server
no ip domain-lookup
no cdp run

! Enable password encryption
service password-encryption

! Configure logging
logging buffered 32768
logging console critical
service timestamps log datetime msec
service timestamps debug datetime msec

! Banner configuration
banner motd ^
*********************************************************
* AUTHORIZED ACCESS ONLY                                 *
* This system is for authorized users only.             *
* All activity is logged and monitored.                 *
* Unauthorized access is strictly prohibited.           *
*********************************************************
^
```

##### 2.2 User Account Configuration
```cisco
! Local user accounts
username admin privilege 15 algorithm-type scrypt secret Admin123!
username neteng privilege 15 algorithm-type scrypt secret NetEng456!

! Enable secret
enable algorithm-type scrypt secret Enable789!

! Console configuration
line console 0
 login local
 exec-timeout 15 0
 logging synchronous
 password Console123!

! VTY configuration  
line vty 0 15
 transport input ssh
 login local
 exec-timeout 15 0
 access-class ADMIN_SSH in
```

##### 2.3 SSH Configuration
```cisco
! Generate RSA key pair
crypto key generate rsa general-keys modulus 2048

! SSH configuration
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
ip ssh logging events

! SSH Access Control List
ip access-list standard ADMIN_SSH
 remark Allow SSH from management subnet
 permit 172.16.10.0 0.0.0.255
 deny any
```

### 🌐 Phase 2: VLAN Implementation

#### Step 3: VLAN Creation & Assignment

##### 3.1 VLAN Database Configuration
```cisco
! Create VLANs
vlan 10
 name Management
 exit

vlan 20  
 name LAN_Users
 exit

vlan 50
 name WLAN_Users  
 exit

vlan 199
 name Blackhole
 shutdown
 exit
```

##### 3.2 Access Port Configuration
```cisco
! Faculty switch access ports (Example: Health & Sciences)
interface range fastethernet 0/1-24
 description Health Sciences Faculty - User Access
 switchport mode access
 switchport access vlan 20
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown

! Wireless controller access port
interface fastethernet 0/25
 description Wireless LAN Controller
 switchport mode access  
 switchport access vlan 50
 spanning-tree portfast
 no shutdown

! Management access port
interface fastethernet 0/26
 description Network Management  
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown
```

##### 3.3 Trunk Port Configuration
```cisco
! Uplink to core switches
interface range gigabitethernet 0/47-48
 description Trunk to Core Switches
 switchport mode trunk
 switchport trunk allowed vlan 10,20,50
 switchport trunk native vlan 999
 channel-group 1 mode active
 no shutdown
```

##### 3.4 Spanning Tree Enhancements
```cisco
! Enable Rapid PVST+
spanning-tree mode rapid-pvst

! Root bridge configuration (Primary Core Switch)
spanning-tree vlan 10,20,50 root primary

! Root bridge configuration (Secondary Core Switch)  
spanning-tree vlan 10,20,50 root secondary

! Global STP settings
spanning-tree portfast default
spanning-tree portfast bpduguard default
spanning-tree extend system-id
```

### 🔗 Phase 3: Link Aggregation

#### Step 4: EtherChannel Configuration

##### 4.1 Access Layer EtherChannels
```cisco
! Configure port-channel interfaces
interface port-channel 1
 description Link to Core Switches
 switchport mode trunk
 switchport trunk allowed vlan 10,20,50
 switchport trunk native vlan 999

! LACP configuration on member interfaces
interface range gigabitethernet 0/47-48
 channel-group 1 mode active
 channel-protocol lacp
```

##### 4.2 Core Layer EtherChannels  
```cisco
! Inter-core switch link aggregation
interface port-channel 2
 description Inter-Core Switch Link
 switchport mode trunk
 switchport trunk allowed vlan all

interface range gigabitethernet 0/1-2
 channel-group 2 mode active
 channel-protocol lacp
```

### 🌐 Phase 4: IP Addressing & Routing

#### Step 5: Layer 3 Interface Configuration

##### 5.1 Core Switch SVI Configuration
```cisco
! Management VLAN interface
interface vlan 10
 description Management Network
 ip address 172.16.10.2 255.255.255.0
 ip helper-address 10.20.20.10
 ip helper-address 10.20.20.11
 standby 10 ip 172.16.10.1
 standby 10 priority 110
 standby 10 preempt
 standby 10 authentication md5 key-string cisco123
 no shutdown

! LAN Users VLAN interface
interface vlan 20
 description LAN Users Network
 ip address 192.168.0.2 255.255.0.0
 ip helper-address 10.20.20.10  
 ip helper-address 10.20.20.11
 standby 20 ip 192.168.0.1
 standby 20 priority 110
 standby 20 preempt
 standby 20 authentication md5 key-string cisco123
 no shutdown

! WLAN Users VLAN interface
interface vlan 50
 description WLAN Users Network
 ip address 10.10.0.2 255.255.0.0
 ip helper-address 10.20.20.10
 ip helper-address 10.20.20.11  
 standby 50 ip 10.10.0.1
 standby 50 priority 110
 standby 50 preempt
 standby 50 authentication md5 key-string cisco123
 no shutdown
```

##### 5.2 Firewall Interface Configuration
```cisco
! Outside interface (Internet-facing)
interface gigabitethernet 0/0
 nameif outside
 security-level 0
 ip address 105.100.50.2 255.255.255.252
 no shutdown

! Inside interface (Internal network)
interface gigabitethernet 0/1
 nameif inside
 security-level 100
 ip address 10.20.20.33 255.255.255.252
 no shutdown

! DMZ interface (Server farm)
interface gigabitethernet 0/2
 nameif dmz
 security-level 50
 ip address 10.20.20.1 255.255.255.224
 no shutdown
```

#### Step 6: HSRP Configuration

##### 6.1 High Availability Setup
```cisco
! Primary core switch HSRP configuration
interface vlan 10
 standby version 2
 standby 10 ip 172.16.10.1
 standby 10 priority 110
 standby 10 preempt delay minimum 30
 standby 10 authentication md5 key-string 7 045802150C2E
 standby 10 track gigabitethernet 0/1 20

! Secondary core switch HSRP configuration
interface vlan 10  
 standby version 2
 standby 10 ip 172.16.10.1
 standby 10 priority 100
 standby 10 preempt delay minimum 30
 standby 10 authentication md5 key-string 7 045802150C2E
```

### 🖥️ Phase 5: Server Configuration

#### Step 7: DMZ Server Setup

##### 7.1 DHCP Server Configuration
```cisco
! Primary DHCP Server (10.20.20.10)
ip dhcp pool MANAGEMENT
 network 172.16.10.0 255.255.255.0
 default-router 172.16.10.1
 dns-server 10.20.20.12 8.8.8.8
 domain-name campus.university.edu
 lease 1 0 0

ip dhcp pool LAN_USERS
 network 192.168.0.0 255.255.0.0
 default-router 192.168.0.1
 dns-server 10.20.20.12 8.8.8.8
 domain-name campus.university.edu
 lease 0 8 0

ip dhcp pool WLAN_USERS
 network 10.10.0.0 255.255.0.0
 default-router 10.10.0.1
 dns-server 10.20.20.12 8.8.8.8
 domain-name wireless.university.edu
 lease 0 4 0

! DHCP exclusions
ip dhcp excluded-address 172.16.10.1 172.16.10.9
ip dhcp excluded-address 192.168.0.1 192.168.0.254
ip dhcp excluded-address 10.10.0.1 10.10.0.254
```

### 🔄 Phase 6: Dynamic Routing

#### Step 8: OSPF Configuration

##### 8.1 OSPF Process Configuration
```cisco
! Core switch OSPF configuration
router ospf 1
 router-id 1.1.1.1
 area 0 authentication message-digest
 passive-interface default
 no passive-interface gigabitethernet 0/3
 network 172.16.10.0 0.0.0.255 area 0
 network 192.168.0.0 0.0.255.255 area 0
 network 10.10.0.0 0.0.255.255 area 0
 network 10.20.20.32 0.0.0.3 area 0
 default-information originate

! Interface authentication
interface gigabitethernet 0/3
 ip ospf message-digest-key 1 md5 ospf123
 ip ospf network point-to-point
 ip ospf hello-interval 10
 ip ospf dead-interval 40
```

##### 8.2 Firewall OSPF Configuration
```cisco
! ASA OSPF configuration  
router ospf 1
 router-id 2.2.2.2
 area 0 authentication message-digest
 network 10.20.20.32 255.255.255.252 area 0
 network 10.20.20.36 255.255.255.252 area 0
 default-information originate

! Interface OSPF settings
interface gigabitethernet 0/1
 ospf message-digest-key 1 md5 ospf123
 ospf network point-to-point
```

### 🛡️ Phase 7: Firewall Security

#### Step 9: ASA Security Configuration

##### 9.1 Basic Security Settings
```cisco
! Object groups for servers
object-group network DMZ_SERVERS
 network-object host 10.20.20.10
 network-object host 10.20.20.11
 network-object host 10.20.20.12
 network-object host 10.20.20.13

object-group service WEB_SERVICES tcp
 port-object eq www
 port-object eq https

object-group service EMAIL_SERVICES tcp
 port-object eq smtp  
 port-object eq pop3
 port-object eq imap
```

##### 9.2 Access Control Lists
```cisco
! Outside to DMZ access
access-list OUTSIDE_IN extended permit tcp any object-group DMZ_SERVERS object-group WEB_SERVICES
access-list OUTSIDE_IN extended permit tcp any host 10.20.20.14 object-group EMAIL_SERVICES
access-list OUTSIDE_IN extended permit udp any host 10.20.20.12 eq domain
access-list OUTSIDE_IN extended deny ip any any log

! Apply ACL to interface
access-group OUTSIDE_IN in interface outside

! DMZ to Inside access (limited)
access-list DMZ_IN extended permit tcp host 10.20.20.17 192.168.0.0 255.255.0.0 eq 3306
access-list DMZ_IN extended deny ip any any log
access-group DMZ_IN in interface dmz
```

##### 9.3 NAT Configuration
```cisco
! Auto NAT for inside networks
object network INSIDE_NETWORK
 subnet 192.168.0.0 255.255.0.0
 nat (inside,outside) dynamic interface

object network WLAN_NETWORK
 subnet 10.10.0.0 255.255.0.0
 nat (inside,outside) dynamic interface

! Static NAT for DMZ servers
object network WEB_SERVER
 host 10.20.20.13
 nat (dmz,outside) static 105.100.50.10

object network EMAIL_SERVER
 host 10.20.20.14  
 nat (dmz,outside) static 105.100.50.11
```

### 📡 Phase 8: Wireless Configuration

#### Step 10: Cisco WLC Setup

##### 10.1 Basic WLC Configuration
```cisco
! Initial setup via GUI or CLI
config network interface address management 172.16.10.5 255.255.255.0 172.16.10.1
config network interface dhcp management primary 10.20.20.10

! WLAN creation
config wlan create 1 Campus_WiFi Campus_WiFi
config wlan interface 1 management
config wlan broadcast-ssid enable 1

! Security configuration
config wlan security wpa akm 802.1x enable 1
config wlan security wpa akm psk disable 1
config wlan security encryption aes enable 1
config wlan radius auth add 1 172.16.10.20 1812 ascii Radius123!

! Enable WLAN
config wlan enable 1
```

##### 10.2 Access Point Configuration
```cisco
! AP join configuration
config ap primary-base HQ-WLC-01 AP-Health-Sciences-01
config ap lwapp-transport-mode 1 AP-Health-Sciences-01

! AP radio configuration
config 802.11a enable AP-Health-Sciences-01  
config 802.11b enable AP-Health-Sciences-01
config ap power global auto
config ap channel global auto
```

### 🔐 Phase 9: VPN Implementation

#### Step 11: IPsec VPN Configuration

##### 11.1 Main Campus Firewall VPN Setup
```cisco
! Phase 1 configuration
crypto isakmp policy 10
 authentication pre-share
 encryption aes 256
 hash sha256  
 group 14
 lifetime 86400

crypto isakmp key VpnKey123! address 205.200.100.2

! Phase 2 configuration
crypto ipsec transform-set VPN_SET esp-aes 256 esp-sha256-hmac

! Crypto map configuration
access-list VPN_TRAFFIC extended permit ip 192.168.0.0 255.255.0.0 192.168.100.0 255.255.255.0
access-list VPN_TRAFFIC extended permit ip 10.10.0.0 255.255.0.0 10.11.0.0 255.255.0.0

crypto map VPN_MAP 10 ipsec-isakmp
 set peer 205.200.100.2
 set transform-set VPN_SET
 set pfs group14
 match address VPN_TRAFFIC

interface gigabitethernet 0/0
 crypto map VPN_MAP
```

##### 11.2 Branch Campus Firewall VPN Setup
```cisco
! Corresponding configuration for branch campus
crypto isakmp policy 10
 authentication pre-share
 encryption aes 256
 hash sha256
 group 14
 lifetime 86400

crypto isakmp key VpnKey123! address 105.100.50.2

! Transform set and crypto map (mirror configuration)
crypto ipsec transform-set VPN_SET esp-aes 256 esp-sha256-hmac

access-list VPN_TRAFFIC extended permit ip 192.168.100.0 255.255.255.0 192.168.0.0 255.255.0.0
access-list VPN_TRAFFIC extended permit ip 10.11.0.0 255.255.0.0 10.10.0.0 255.255.0.0
```

### ✅ Phase 10: Testing & Validation

#### Step 12: Comprehensive Testing

##### 12.1 Connectivity Testing
```bash
# Basic connectivity tests
ping 172.16.10.1  # Management gateway
ping 192.168.0.1  # LAN gateway  
ping 10.10.0.1    # WLAN gateway
ping 10.20.20.1   # DMZ gateway
ping 8.8.8.8      # Internet connectivity

# Inter-VLAN communication
ping 192.168.0.10 source 10.10.0.10  # WLAN to LAN
ping 172.16.10.10 source 192.168.0.10 # LAN to Management
```

##### 12.2 Service Testing
```bash  
# DHCP functionality
ipconfig /release
ipconfig /renew
ipconfig /all

# DNS resolution
nslookup www.google.com
nslookup campus.university.edu

# Web services
curl -I http://10.20.20.13
telnet 10.20.20.14 25  # SMTP test
```

##### 12.3 VPN Testing
```cisco
# VPN status verification
show crypto isakmp sa
show crypto ipsec sa
show crypto session

# VPN traffic testing
ping 192.168.100.10 source 192.168.0.10
traceroute 10.11.0.10 source 10.10.0.10
```

## 📊 Post-Implementation Validation

### Performance Baselines
- **Latency**: < 5ms intra-campus, < 50ms inter-campus
- **Throughput**: 95% of interface capacity  
- **CPU Usage**: < 70% average on network devices
- **Memory Usage**: < 80% average on network devices

### Security Verification
- **Access Controls**: Verify ACL effectiveness
- **VPN Encryption**: Confirm tunnel establishment
- **Port Security**: Test violation responses
- **Authentication**: Validate SSH access restrictions

---

> ⚙️ **Implementation Status**: Complete | 🎯 **Validation**: Passed | 🔒 **Security**: Verified