# 🌐 NAT/PAT and IPv6 Design Documentation

## 📋 Overview

This document details the Network Address Translation (NAT/PAT) implementation and IPv6 readiness strategy
for the Secure Campus Network System.

## 🔄 NAT/PAT Implementation

### Design Philosophy

- **Dynamic PAT (Port Address Translation)**: For all outbound internet traffic from internal users
- **Static NAT**: For DMZ servers requiring inbound access from the internet
- **Policy NAT**: For specific traffic flows requiring different translation rules

### Translation Architecture

```
Internet (Public IPs)
       ↕
[ASA Firewall] - NAT/PAT Engine
       ↕
Internal Networks (RFC 1918)
```

## 🔢 IP Address Pools

### Public IP Allocation

| Service Type | Public IP Range | Purpose | Count |
| ------------ | --------------- | ------- | ----- |
| **Main Campus WAN** | `105.100.50.0/30` | Internet connectivity | 2 usable |
| **Branch Campus WAN** | `205.200.100.0/30` | Internet connectivity | 2 usable |
| **DMZ Server Pool** | `105.100.50.8/29` | Static NAT for servers | 6 usable |

### Public IP Assignment

| Server | Internal IP | Public IP | Services |
| ------ | ----------- | --------- | -------- |
| **Web Server** | `172.16.100.10` | `105.100.50.10` | HTTP, HTTPS |
| **Mail Server** | `172.16.100.15` | `105.100.50.15` | SMTP, IMAP, POP3 |
| **DNS Server** | `172.16.100.20` | `105.100.50.20` | DNS (UDP/TCP 53) |
| **FTP Server** | `172.16.100.25` | `105.100.50.25` | FTP, FTPS |
| **VPN Concentrator** | `172.16.100.30` | `105.100.50.30` | IPsec VPN |
| **Backup/Future** | - | `105.100.50.11-14` | Reserved |

## 🔒 Dynamic PAT Configuration

### Main Campus PAT

```cisco
! ASA Configuration
object network INSIDE_NAT
 subnet 0.0.0.0 0.0.0.0
 nat (inside,outside) dynamic interface

! This translates all internal traffic to the outside interface IP
! Source: Any internal network (192.168.x.x, 10.x.x.x)
! Destination: Internet
! Translation: 105.100.50.2 (with dynamic port assignment)
```

### Faculty Networks PAT

All faculty networks share the same dynamic PAT pool:

- Health & Sciences: `192.168.20.0/22`, `10.20.0.0/20`
- Business: `192.168.30.0/22`, `10.30.0.0/20`
- Engineering: `192.168.40.0/22`, `10.40.0.0/20`
- Art/Design: `192.168.50.0/22`, `10.50.0.0/20`
- Guest WiFi: `10.100.0.0/20`
- Voice: `10.240.0.0/20`

All translate to: `105.100.50.2` with PAT

### Connection Limits

- **Maximum concurrent connections**: 100,000
- **Connection timeout**: 1 hour for established TCP
- **Half-closed timeout**: 10 minutes
- **UDP timeout**: 2 minutes

## 📌 Static NAT Rules

### Web Server (1:1 NAT)

```cisco
object network WEB_SERVER
 host 172.16.100.10
 nat (dmz,outside) static 105.100.50.10

! Inbound Access List
access-list OUTSIDE_IN extended permit tcp any host 105.100.50.10 eq 80
access-list OUTSIDE_IN extended permit tcp any host 105.100.50.10 eq 443
```

**Translation Flow:**
- External client connects to `105.100.50.10:443`
- ASA translates to `172.16.100.10:443`
- Return traffic automatically translated back

### Mail Server (with Port Forwarding)

```cisco
object network MAIL_SERVER
 host 172.16.100.15
 nat (dmz,outside) static 105.100.50.15

! Inbound rules for mail services
access-list OUTSIDE_IN extended permit tcp any host 105.100.50.15 eq smtp
access-list OUTSIDE_IN extended permit tcp any host 105.100.50.15 eq 587
access-list OUTSIDE_IN extended permit tcp any host 105.100.50.15 eq 993
access-list OUTSIDE_IN extended permit tcp any host 105.100.50.15 eq 995
```

### DNS Server (UDP and TCP)

```cisco
object network DNS_SERVER
 host 172.16.100.20
 nat (dmz,outside) static 105.100.50.20

! DNS requires both UDP and TCP
access-list OUTSIDE_IN extended permit udp any host 105.100.50.20 eq domain
access-list OUTSIDE_IN extended permit tcp any host 105.100.50.20 eq domain
```

## 🌍 IPv6 Readiness Strategy

### Current State (IPv4-Only)

The network currently operates in IPv4-only mode with RFC 1918 private addressing internally
and NAT for internet connectivity.

### IPv6 Transition Plan

#### Phase 1: Infrastructure Preparation (Year 1)

1. **Device Compatibility Audit**
   - Verify all core switches support IPv6 routing
   - Confirm firewall supports IPv6 ACLs and stateful inspection
   - Check router IOS versions for IPv6 capabilities

2. **Addressing Plan Development**
   - Obtain IPv6 prefix from ISP (recommended: /48 or /56)
   - Design IPv6 addressing scheme parallel to IPv4
   - Plan subnet allocation for each faculty

#### Phase 2: Dual-Stack Implementation (Year 2)

1. **Enable IPv6 on Core Infrastructure**
   ```cisco
   ! Core Switch
   ipv6 unicast-routing
   ipv6 cef
   
   interface Vlan20
    ipv6 address 2001:db8:1:20::1/64
    ipv6 nd prefix 2001:db8:1:20::/64
    ipv6 dhcp server DHCPV6_POOL
   ```

2. **Configure DHCPv6 and SLAAC**
   - Implement Stateless Address Autoconfiguration (SLAAC)
   - Deploy DHCPv6 for managed addressing
   - Configure DNS servers with AAAA records

3. **Firewall IPv6 Support**
   ```cisco
   ! ASA Firewall
   ipv6 access-list IPV6_OUTSIDE_IN
    permit icmp any any
    permit tcp any host 2001:db8:1:100::10 eq 443
    deny ipv6 any any log
   
   interface GigabitEthernet0/0
    ipv6 address 2001:db8:1:999::2/64
    ipv6 enable
   ```

#### Phase 3: IPv6 Security Hardening (Year 3)

1. **Implement IPv6 ACLs**
   - Restrict ICMPv6 (allow only necessary types)
   - Block IPv6 tunneling protocols at perimeter
   - Implement RA Guard on access switches

2. **IPv6 Monitoring and Logging**
   - Configure NetFlow v9 for IPv6 traffic
   - Monitor for unauthorized IPv6 traffic
   - Implement IPv6-aware IDS/IPS

### Proposed IPv6 Addressing Scheme

Assuming ISP allocation: `2001:db8:1::/48`

| Network | IPv6 Prefix | Description |
| ------- | ----------- | ----------- |
| **Management** | `2001:db8:1:10::/64` | Device management |
| **Health Sciences LAN** | `2001:db8:1:20::/64` | Faculty wired |
| **Health Sciences WLAN** | `2001:db8:1:21::/64` | Faculty wireless |
| **Business LAN** | `2001:db8:1:30::/64` | Faculty wired |
| **Business WLAN** | `2001:db8:1:31::/64` | Faculty wireless |
| **Engineering LAN** | `2001:db8:1:40::/64` | Faculty wired |
| **Engineering WLAN** | `2001:db8:1:41::/64` | Faculty wireless |
| **Art/Design LAN** | `2001:db8:1:50::/64` | Faculty wired |
| **Art/Design WLAN** | `2001:db8:1:51::/64` | Faculty wireless |
| **DMZ Servers** | `2001:db8:1:100::/64` | Public servers |
| **VoIP** | `2001:db8:1:240::/64` | IP telephony |
| **Guest WiFi** | `2001:db8:1:254::/64` | Guest access |

### IPv6 Security Considerations

1. **No More NAT Hiding**: IPv6 end-to-end connectivity requires explicit firewall rules
2. **ICMPv6 is Critical**: Cannot block all ICMPv6 like with IPv4
3. **Privacy Extensions**: Implement RFC 4941 for user privacy
4. **DHCPv6 Guard**: Prevent rogue DHCPv6 servers
5. **IPv6 First-Hop Security**: Implement RA Guard, DHCPv6 Guard, IPv6 Source Guard

## 📊 NAT/PAT Performance Metrics

### Current Capacity

| Metric | Value | Threshold |
| ------ | ----- | --------- |
| **Max Translations** | 100,000 | 80% alert |
| **Active Connections** | Monitor | 75,000 warning |
| **Translation Rate** | 500/sec | 400/sec alert |
| **Port Exhaustion** | Monitor | < 1000 ports free |

### Monitoring Commands

```cisco
! ASA Firewall
show xlate count
show conn count
show nat
show nat detail
show local-host

! Check specific translations
show xlate local 192.168.20.100
show conn detail | include 192.168.20.100
```

## 🔧 Troubleshooting NAT Issues

### Common Issues

1. **Port Exhaustion**
   - Symptom: Users cannot establish new connections
   - Cause: All 65,535 ports in use on public IP
   - Solution: Reduce connection timeouts, add more public IPs

2. **Asymmetric Routing**
   - Symptom: Connections timeout, half-open states
   - Cause: Return traffic takes different path
   - Solution: Implement PBR (Policy-Based Routing)

3. **Application Layer Issues**
   - Symptom: FTP, SIP, H.323 calls fail
   - Cause: Application-layer protocol requires inspection
   - Solution: Enable ASA protocol inspection

### Verification Steps

```cisco
! Verify NAT is working
show nat detail | include hits
show xlate | include 192.168.20.100

! Debug NAT (use with caution in production)
debug nat
debug packet inside
```

## 📝 Best Practices

### NAT Design

1. ✅ **Use PAT for user traffic** - Conserves public IPs
2. ✅ **Static NAT for servers** - Consistent inbound access
3. ✅ **Monitor port usage** - Prevent exhaustion
4. ✅ **Document all static NAT** - For troubleshooting
5. ✅ **Implement connection limits** - Prevent DoS

### IPv6 Preparation

1. ✅ **Plan addressing carefully** - Difficult to change later
2. ✅ **Test in lab first** - Dual-stack can be complex
3. ✅ **Train staff on IPv6** - Different troubleshooting
4. ✅ **Update documentation** - Include IPv6 addresses
5. ✅ **Monitor both stacks** - Ensure parity

## 🎯 Future Enhancements

### Short Term (6-12 months)

- [ ] Implement NAT logging for compliance
- [ ] Add redundant public IP pool
- [ ] Configure NAT failover with HSRP
- [ ] Implement NAT64 for IPv6-only clients

### Long Term (1-2 years)

- [ ] Full dual-stack deployment
- [ ] Transition to IPv6-primary with NAT64
- [ ] Retire IPv4 for internal traffic
- [ ] Implement IPv6-only guest network

## 📚 References

- **RFC 1918**: Address Allocation for Private Internets
- **RFC 2663**: IP Network Address Translator (NAT) Terminology and Considerations
- **RFC 4787**: Network Address Translation (NAT) Behavioral Requirements for Unicast UDP
- **RFC 6146**: Stateful NAT64
- **RFC 8200**: Internet Protocol, Version 6 (IPv6) Specification
- **RFC 4941**: Privacy Extensions for Stateless Address Autoconfiguration in IPv6

---

> 🌐 **NAT Status**: Production Ready | 🌍 **IPv6 Status**: Planned Dual-Stack
