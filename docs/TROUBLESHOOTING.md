# 🔧 Troubleshooting Guide

## 🚨 Common Issues and Solutions

This comprehensive troubleshooting guide covers common issues you may encounter in the Secure Campus Network System and provides step-by-step solutions.

## 📋 Quick Reference

### Emergency Contacts
- **Network Operations Center**: [Phone Number]
- **ISP Support (Airtel)**: [Phone Number]
- **Cisco TAC**: 1-800-553-2447
- **Senior Network Engineer**: [Phone Number]

### Critical Command Quick Reference
```cisco
! Show commands for quick diagnosis
show ip route                    ! Routing table
show ip interface brief          ! Interface status
show spanning-tree summary       ! STP status
show etherchannel summary        ! Link aggregation
show standby brief               ! HSRP status
show crypto session              ! VPN status
```

## 🌐 Connectivity Issues

### Issue 1: No Internet Access

#### Symptoms
- Users cannot browse the internet
- DNS resolution fails
- Ping to 8.8.8.8 fails

#### Diagnosis Steps
```cisco
! Step 1: Check default route
show ip route 0.0.0.0

! Step 2: Check firewall NAT
show xlate

! Step 3: Check ISP connectivity
ping 105.100.50.1
ping 205.200.100.1

! Step 4: Check DNS servers
nslookup google.com 8.8.8.8
```

#### Common Causes & Solutions

**Cause 1: Default Route Missing**
```cisco
! Solution: Add default route on firewall
route outside 0.0.0.0 0.0.0.0 105.100.50.1 1

! On core switches
ip route 0.0.0.0 0.0.0.0 10.20.20.33
```

**Cause 2: NAT Configuration Issue**
```cisco
! Check NAT configuration
show nat

! Fix NAT for internal networks
object network INSIDE_NET
 subnet 192.168.0.0 255.255.0.0
 nat (inside,outside) dynamic interface
```

**Cause 3: DNS Server Down**
```cisco
! Check DNS server status
ping 10.20.20.12

! Update DNS settings if needed
ip dhcp pool LAN_USERS
 dns-server 8.8.8.8 8.8.4.4
```

### Issue 2: Inter-VLAN Communication Failure

#### Symptoms
- Users in different VLANs cannot communicate
- PING fails between VLANs
- Services in DMZ unreachable from LAN

#### Diagnosis Steps
```cisco
! Check VLAN configuration
show vlan brief

! Check SVI status
show ip interface brief | include Vlan

! Check routing between VLANs
show ip route connected

! Check HSRP status
show standby brief
```

#### Solutions

**VLAN Interface Down:**
```cisco
interface vlan 20
 no shutdown
 ip address 192.168.0.2 255.255.0.0
```

**HSRP Not Active:**
```cisco
! Check HSRP configuration
interface vlan 20
 standby 20 ip 192.168.0.1
 standby 20 priority 110
 standby 20 preempt
```

**Missing Route:**
```cisco
! Add static route if needed
ip route 10.20.20.0 255.255.255.224 10.20.20.33
```

## 🔄 Routing Issues

### Issue 3: OSPF Neighbor Adjacency Problems

#### Symptoms
- OSPF neighbors not forming adjacency
- Routes not being advertised
- Network convergence issues

#### Diagnosis Steps
```cisco
! Check OSPF neighbors
show ip ospf neighbor

! Check OSPF database
show ip ospf database

! Check interface OSPF configuration
show ip ospf interface

! Debug OSPF hello packets (use cautiously)
debug ip ospf hello
```

#### Common Causes & Solutions

**Area Mismatch:**
```cisco
! Verify area configuration
router ospf 1
 network 172.16.10.0 0.0.0.255 area 0
 network 192.168.0.0 0.0.255.255 area 0
```

**Authentication Mismatch:**
```cisco
! Check MD5 authentication
interface gigabitethernet 0/1
 ip ospf message-digest-key 1 md5 ospf123

! Verify area authentication
router ospf 1
 area 0 authentication message-digest
```

**Hello/Dead Timer Mismatch:**
```cisco
! Standardize timers
interface gigabitethernet 0/1
 ip ospf hello-interval 10
 ip ospf dead-interval 40
```

### Issue 4: VPN Tunnel Down

#### Symptoms
- Inter-campus communication fails
- IPsec tunnel not established
- Phase 1 or Phase 2 failures

#### Diagnosis Steps
```cisco
! Check IKE status
show crypto isakmp sa

! Check IPsec status
show crypto ipsec sa

! Check interesting traffic
show access-list VPN_TRAFFIC

! Debug IKE (use cautiously in production)
debug crypto isakmp
debug crypto ipsec
```

#### Solutions

**Phase 1 Issues:**
```cisco
! Verify pre-shared key
crypto isakmp key VpnKey123! address 205.200.100.2

! Check Phase 1 policy
crypto isakmp policy 10
 encryption aes 256
 hash sha256
 authentication pre-share
 group 14
```

**Phase 2 Issues:**
```cisco
! Verify transform set
crypto ipsec transform-set VPN_SET esp-aes 256 esp-sha256-hmac

! Check crypto map
crypto map VPN_MAP 10 ipsec-isakmp
 set peer 205.200.100.2
 set transform-set VPN_SET
 match address VPN_TRAFFIC
```

**Interesting Traffic Issues:**
```cisco
! Verify ACL for VPN traffic
access-list VPN_TRAFFIC extended permit ip 192.168.0.0 255.255.0.0 192.168.100.0 255.255.255.0
```

## 🔌 Switching Issues

### Issue 5: Port Security Violations

#### Symptoms
- Ports shutting down unexpectedly
- Users losing connectivity randomly
- Error messages about MAC address violations

#### Diagnosis Steps
```cisco
! Check port security status
show port-security

! Check specific interface
show port-security interface fastethernet 0/1

! View security violations
show port-security address
```

#### Solutions

**Recover from Violation:**
```cisco
! Re-enable shutdown interface
interface fastethernet 0/1
 shutdown
 no shutdown
```

**Adjust Port Security Settings:**
```cisco
interface fastethernet 0/1
 switchport port-security maximum 3
 switchport port-security violation restrict
```

**Clear Sticky MAC Addresses:**
```cisco
clear port-security sticky interface fastethernet 0/1
```

### Issue 6: Spanning Tree Issues

#### Symptoms
- Network loops causing broadcast storms
- Intermittent connectivity
- High CPU usage on switches

#### Diagnosis Steps
```cisco
! Check STP status
show spanning-tree summary

! Check root bridge
show spanning-tree root

! Check port states
show spanning-tree interface detail

! Check for topology changes
show spanning-tree detail | include Number
```

#### Solutions

**Root Bridge Not Optimal:**
```cisco
! Set priority on desired root bridge
spanning-tree vlan 1-100 priority 4096

! Or use root primary
spanning-tree vlan 1-100 root primary
```

**Port Stuck in Blocking:**
```cisco
! Enable PortFast on access ports
interface range fastethernet 0/1-24
 spanning-tree portfast
```

**BPDU Guard Triggered:**
```cisco
! Reset BPDU guard
interface fastethernet 0/1
 shutdown
 no shutdown
```

## 🔐 Security Issues

### Issue 7: Firewall Access Denied

#### Symptoms
- Legitimate traffic being blocked
- Services unreachable from outside
- Unexpected access denials

#### Diagnosis Steps
```cisco
! Monitor real-time traffic
show conn

! Check NAT translations
show xlate

! Review access lists
show access-list

! Monitor logs
show log | include Deny
```

#### Solutions

**Update Access Control Lists:**
```cisco
! Allow new service
access-list OUTSIDE_IN extended permit tcp any host 10.20.20.15 eq 3389
```

**NAT Configuration Update:**
```cisco
object network RDP_SERVER
 host 10.20.20.15
 nat (dmz,outside) static 105.100.50.15
```

**Security Level Adjustment:**
```cisco
! Adjust security levels if needed
interface gigabitethernet 0/2
 security-level 60
```

### Issue 8: DHCP Pool Exhaustion

#### Symptoms
- New devices cannot get IP addresses
- DHCP DISCOVER packets with no response
- Users reporting "No network access"

#### Diagnosis Steps
```cisco
! Check DHCP bindings
show ip dhcp binding

! Check pool utilization
show ip dhcp pool

! Check for conflicts
show ip dhcp conflict
```

#### Solutions

**Clear Old Bindings:**
```cisco
clear ip dhcp binding *
```

**Expand DHCP Pool:**
```cisco
ip dhcp pool LAN_USERS
 network 192.168.0.0 255.254.0.0  ! Expanded subnet
```

**Adjust Lease Time:**
```cisco
ip dhcp pool LAN_USERS
 lease 0 2 0  ! Reduce to 2 hours
```

## 📡 Wireless Issues

### Issue 9: Wireless Controller Connectivity

#### Symptoms
- APs not joining controller
- Wireless clients cannot associate
- Controller unreachable

#### Diagnosis Steps
```bash
# Check controller status
show sysinfo
show interface summary

# Check AP status
show ap summary
show ap join stats summary

# Check DHCP for AP discovery
show dhcp proxy
```

#### Solutions

**AP Discovery Issues:**
```bash
# Configure DHCP option 43
config dhcp create-scope "AP_Scope" 10.10.0.100 10.10.0.200 255.255.0.0
config dhcp scope AP_Scope option 43 ascii "5A1N;B2;S3;P1"
```

**Controller Interface Down:**
```bash
# Reset management interface
config interface address management 172.16.10.5 255.255.255.0 172.16.10.1
```

## 🔍 Performance Issues

### Issue 10: High CPU/Memory Usage

#### Symptoms
- Slow network response
- Intermittent connectivity
- Device unresponsiveness

#### Diagnosis Steps
```cisco
! Check CPU usage
show processes cpu sorted

! Check memory usage
show memory statistics

! Check interface utilization
show interfaces summary

! Monitor for errors
show interfaces | include error
```

#### Solutions

**High CPU from Routing:**
```cisco
! Implement route filtering
router ospf 1
 area 1 range 192.168.0.0 255.255.0.0
```

**Memory Issues:**
```cisco
! Clear unnecessary logs
clear logging

! Reduce buffer sizes
logging buffered 16384
```

**Interface Errors:**
```cisco
! Check and replace cables
! Verify duplex settings
interface fastethernet 0/1
 duplex full
 speed 100
```

## 🛠️ Diagnostic Tools and Commands

### Network Layer Diagnostics
```cisco
! Layer 1-2 diagnostics
show interfaces status
show mac address-table
show cdp neighbors detail

! Layer 3 diagnostics  
show ip arp
show ip route
ping 8.8.8.8 source vlan 20

! Layer 4-7 diagnostics
telnet 10.20.20.10 80
show ip nat translations
```

### Performance Monitoring
```cisco
! Interface statistics
show interfaces gigabitethernet 0/1 | include rate
show interfaces counters errors

! Protocol statistics
show ip ospf statistics
show crypto ipsec sa | include pkts
```

### Security Monitoring
```cisco
! Access list hit counters
show access-list | include matches

! Port security violations
show port-security | include Violation

! Authentication failures
show logging | include fail
```

## 📞 Escalation Procedures

### Level 1 Issues (Self-Service)
- Basic connectivity problems
- Password resets
- Simple configuration changes
- **Resolution Time**: 15-30 minutes

### Level 2 Issues (Network Team)
- VLAN configuration issues
- Routing problems
- Switch/router failures
- **Resolution Time**: 1-4 hours
- **Escalation**: After 2 hours

### Level 3 Issues (Critical)
- Network-wide outages
- Security incidents
- Hardware failures
- **Resolution Time**: 15 minutes response
- **Immediate Escalation**: Senior management

### Emergency Procedures
1. **Document the Issue**: Time, symptoms, affected users
2. **Initial Assessment**: Determine impact scope
3. **Immediate Actions**: Isolate problem if possible
4. **Communication**: Notify stakeholders
5. **Resolution**: Apply fix and verify
6. **Follow-up**: Document resolution and lessons learned

---

> 🔧 **Troubleshooting**: Comprehensive | 🚨 **Emergency Response**: Ready | 📞 **Escalation**: Defined