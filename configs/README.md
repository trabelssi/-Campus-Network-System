# 📁 Configuration Files

This directory contains device configuration files organized by device type.

## 📂 Directory Structure

- **switches/** - Cisco Catalyst switch configurations
- **firewalls/** - Cisco ASA firewall configurations  
- **wireless/** - Cisco WLC and wireless configurations

## 🔧 Configuration Standards

All configuration files follow these standards:

### File Naming Convention
```
[CAMPUS]-[ROLE]-[MODEL]-[ID].cfg

Examples:
- HQ-CORE-SW-01.cfg (Main campus core switch)
- BR-ASA-FW-01.cfg (Branch campus firewall)
- HQ-WLC-01.cfg (Main campus wireless controller)
```

### Configuration Headers
```cisco
! ================================================================
! Device: [HOSTNAME] 
! Location: [CAMPUS] - [BUILDING] - [ROOM]
! Role: [DEVICE_ROLE]
! Model: [DEVICE_MODEL]
! Last Modified: [DATE]
! Modified By: [ENGINEER_NAME]
! Version: [CONFIG_VERSION]
! ================================================================
```

## 🚀 Usage

### Backup Existing Configurations
```bash
# Use the backup script
python scripts/backup-configs.py

# Or manual backup via SSH
scp admin@device-ip:system:running-config configs/switches/device-name.cfg
```

### Deploy Configurations  
```bash
# Copy configuration to device
scp configs/switches/HQ-CORE-SW-01.cfg admin@172.16.10.2:

# Apply via console/SSH
copy tftp://server/config running-config
```

### Validate Configurations
```bash
# Check syntax (if validation tools available)
python scripts/config-validator.py configs/switches/

# Test connectivity after deployment
python scripts/network-monitoring.py --device HQ-CORE-SW-01
```

## 📋 Configuration Checklist

Before deploying any configuration:

- [ ] Configuration follows naming convention
- [ ] Header information is complete and accurate
- [ ] Sensitive information (passwords) is properly secured
- [ ] Configuration has been tested in lab environment
- [ ] Backup of existing configuration taken
- [ ] Change management approval obtained
- [ ] Rollback procedure documented

## 🔐 Security Notes

- **Never commit real passwords** to version control
- Use **placeholder passwords** in shared configurations
- Store **actual credentials** in secure credential management system
- **Encrypt sensitive** configuration sections when possible

## 📞 Support

For configuration questions or issues:
- Review [Configuration Guide](../docs/implementation/configuration-guide.md)
- Check [Troubleshooting Guide](../docs/TROUBLESHOOTING.md)  
- Contact network engineering team

---

> 🔧 **Configuration Management** | 📁 **Organized Structure** | 🔒 **Security Focused**