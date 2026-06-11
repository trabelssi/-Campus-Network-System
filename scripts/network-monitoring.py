#!/usr/bin/env python3
"""
Network Monitoring Script for Secure Campus Network System
Author: Trabelsi Mohamed Amine
Academic Project: Master's Degree - Network Engineering
Description: Automated monitoring and health checking for campus network infrastructure
Version: 1.0.0
"""

import subprocess
import socket
import time
import json
import smtplib
import logging
from datetime import datetime
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import paramiko
import requests

# Configuration
CONFIG = {
    'devices': {
        'HQ-CORE-SW01': {
            'ip': '172.16.10.2',
            'type': 'switch',
            'username': 'admin',
            'password': 'Admin123!',  # In production, use secure credential management
            'community': 'ReadOnly'
        },
        'HQ-CORE-SW02': {
            'ip': '172.16.10.3',
            'type': 'switch',
            'username': 'admin',
            'password': 'Admin123!',
            'community': 'ReadOnly'
        },
        'HQ-ASA-FW01': {
            'ip': '172.16.10.4',
            'type': 'firewall',
            'username': 'admin',
            'password': 'Admin123!',
            'community': 'ReadOnly'
        },
        'HQ-WLC-01': {
            'ip': '172.16.10.5',
            'type': 'wlc',
            'username': 'admin',
            'password': 'Admin123!',
            'community': 'ReadOnly'
        }
    },
    'monitoring': {
        'ping_timeout': 5,
        'ssh_timeout': 10,
        'snmp_timeout': 5,
        'check_interval': 300,  # 5 minutes
        'alert_threshold': 3,   # 3 consecutive failures
        'log_file': 'network_monitoring.log',
        'alert_email': 'network-admin@university.edu',
        'smtp_server': '10.20.20.14',
        'smtp_port': 587
    },
    'thresholds': {
        'cpu_warning': 70,
        'cpu_critical': 85,
        'memory_warning': 75,
        'memory_critical': 90,
        'interface_utilization': 80,
        'ping_loss_warning': 10,
        'ping_loss_critical': 25
    }
}

# Setup logging
logging.basicConfig(
    filename=CONFIG['monitoring']['log_file'],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class NetworkMonitor:
    def __init__(self):
        self.device_status = {}
        self.failure_counts = {}
        self.alerts_sent = set()
        
    def ping_test(self, host, timeout=5):
        """Perform ping test to check basic connectivity"""
        try:
            # Windows ping command
            result = subprocess.run(
                ['ping', '-n', '4', '-w', str(timeout * 1000), host],
                capture_output=True,
                text=True,
                timeout=timeout + 5
            )
            
            if result.returncode == 0:
                # Parse ping statistics
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'Lost =' in line:
                        # Extract packet loss percentage
                        loss_str = line.split('Lost = ')[1].split(' (')[1].split('%')[0]
                        loss_percent = int(loss_str)
                        return {
                            'status': 'success',
                            'packet_loss': loss_percent,
                            'reachable': True
                        }
                
                return {'status': 'success', 'packet_loss': 0, 'reachable': True}
            else:
                return {'status': 'failed', 'packet_loss': 100, 'reachable': False}
                
        except Exception as e:
            logging.error(f"Ping test failed for {host}: {str(e)}")
            return {'status': 'error', 'packet_loss': 100, 'reachable': False}

    def ssh_check(self, device_name, device_config):
        """Check SSH connectivity and gather device information"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(
                hostname=device_config['ip'],
                username=device_config['username'],
                password=device_config['password'],
                timeout=CONFIG['monitoring']['ssh_timeout']
            )
            
            # Execute basic health check commands
            health_data = {}
            
            if device_config['type'] in ['switch', 'router']:
                # Get system information
                stdin, stdout, stderr = ssh.exec_command('show version | include uptime')
                uptime_output = stdout.read().decode().strip()
                health_data['uptime'] = uptime_output
                
                # Get CPU usage
                stdin, stdout, stderr = ssh.exec_command('show processes cpu | include CPU utilization')
                cpu_output = stdout.read().decode().strip()
                health_data['cpu'] = self.parse_cpu_usage(cpu_output)
                
                # Get memory usage
                stdin, stdout, stderr = ssh.exec_command('show memory statistics | include Processor')
                memory_output = stdout.read().decode().strip()
                health_data['memory'] = self.parse_memory_usage(memory_output)
                
                # Get interface status
                stdin, stdout, stderr = ssh.exec_command('show interfaces summary')
                interface_output = stdout.read().decode().strip()
                health_data['interfaces'] = self.parse_interface_summary(interface_output)
            
            elif device_config['type'] == 'firewall':
                # ASA specific commands
                stdin, stdout, stderr = ssh.exec_command('show cpu usage')
                cpu_output = stdout.read().decode().strip()
                health_data['cpu'] = self.parse_asa_cpu_usage(cpu_output)
                
                stdin, stdout, stderr = ssh.exec_command('show memory')
                memory_output = stdout.read().decode().strip()
                health_data['memory'] = self.parse_asa_memory_usage(memory_output)
                
                # Check VPN status
                stdin, stdout, stderr = ssh.exec_command('show crypto session')
                vpn_output = stdout.read().decode().strip()
                health_data['vpn_sessions'] = self.parse_vpn_sessions(vpn_output)
            
            elif device_config['type'] == 'wlc':
                # WLC specific commands
                stdin, stdout, stderr = ssh.exec_command('show sysinfo')
                sysinfo_output = stdout.read().decode().strip()
                health_data['system_info'] = sysinfo_output
                
                stdin, stdout, stderr = ssh.exec_command('show ap summary')
                ap_output = stdout.read().decode().strip()
                health_data['access_points'] = self.parse_ap_summary(ap_output)
            
            ssh.close()
            
            return {
                'status': 'success',
                'ssh_accessible': True,
                'health_data': health_data
            }
            
        except Exception as e:
            logging.error(f"SSH check failed for {device_name}: {str(e)}")
            return {
                'status': 'failed',
                'ssh_accessible': False,
                'error': str(e)
            }

    def parse_cpu_usage(self, cpu_output):
        """Parse CPU usage from show processes cpu output"""
        try:
            # Example: "CPU utilization for five seconds: 15%/2%; one minute: 14%; five minutes: 12%"
            if 'five seconds:' in cpu_output:
                cpu_str = cpu_output.split('five seconds: ')[1].split('%')[0]
                return int(cpu_str.split('/')[0])
            return 0
        except:
            return 0

    def parse_memory_usage(self, memory_output):
        """Parse memory usage from show memory statistics output"""
        try:
            # Parse Cisco memory output format
            lines = memory_output.split('\n')
            for line in lines:
                if 'Processor' in line and 'Total:' in line:
                    # Extract used percentage
                    parts = line.split()
                    if len(parts) >= 5:
                        used = int(parts[2])
                        total = int(parts[1])
                        return round((used / total) * 100, 2)
            return 0
        except:
            return 0

    def parse_asa_cpu_usage(self, cpu_output):
        """Parse ASA CPU usage"""
        try:
            # ASA CPU output format
            lines = cpu_output.split('\n')
            for line in lines:
                if 'CPU utilization' in line:
                    cpu_percent = int(line.split('%')[0].split()[-1])
                    return cpu_percent
            return 0
        except:
            return 0

    def parse_asa_memory_usage(self, memory_output):
        """Parse ASA memory usage"""
        try:
            lines = memory_output.split('\n')
            for line in lines:
                if 'Used memory:' in line and 'Total memory:' in line:
                    used = int(line.split('Used memory: ')[1].split(' bytes')[0])
                    total = int(line.split('Total memory: ')[1].split(' bytes')[0])
                    return round((used / total) * 100, 2)
            return 0
        except:
            return 0

    def parse_vpn_sessions(self, vpn_output):
        """Parse VPN session information"""
        try:
            session_count = vpn_output.count('Session Type:')
            return session_count
        except:
            return 0

    def parse_interface_summary(self, interface_output):
        """Parse interface status summary"""
        try:
            interfaces = {
                'total': 0,
                'up': 0,
                'down': 0,
                'error': 0
            }
            
            lines = interface_output.split('\n')
            for line in lines:
                if 'FastEthernet' in line or 'GigabitEthernet' in line:
                    interfaces['total'] += 1
                    if 'up' in line.lower():
                        interfaces['up'] += 1
                    elif 'down' in line.lower():
                        interfaces['down'] += 1
                    elif 'err' in line.lower():
                        interfaces['error'] += 1
            
            return interfaces
        except:
            return {'total': 0, 'up': 0, 'down': 0, 'error': 0}

    def parse_ap_summary(self, ap_output):
        """Parse wireless access point summary"""
        try:
            ap_stats = {
                'total': 0,
                'registered': 0,
                'unregistered': 0
            }
            
            lines = ap_output.split('\n')
            for line in lines:
                if 'AP Name' not in line and len(line.strip()) > 0:
                    ap_stats['total'] += 1
                    if 'Registered' in line:
                        ap_stats['registered'] += 1
                    else:
                        ap_stats['unregistered'] += 1
            
            return ap_stats
        except:
            return {'total': 0, 'registered': 0, 'unregistered': 0}

    def check_device_health(self, device_name, device_config):
        """Comprehensive device health check"""
        health_report = {
            'device': device_name,
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'checks': {}
        }
        
        # Ping test
        ping_result = self.ping_test(device_config['ip'])
        health_report['checks']['ping'] = ping_result
        
        if ping_result['reachable']:
            # SSH check if ping successful
            ssh_result = self.ssh_check(device_name, device_config)
            health_report['checks']['ssh'] = ssh_result
            
            if ssh_result['ssh_accessible']:
                health_report['status'] = 'healthy'
                health_data = ssh_result.get('health_data', {})
                
                # Check thresholds
                alerts = []
                
                # CPU check
                cpu_usage = health_data.get('cpu', 0)
                if cpu_usage > CONFIG['thresholds']['cpu_critical']:
                    alerts.append(f"Critical: CPU usage {cpu_usage}% (threshold: {CONFIG['thresholds']['cpu_critical']}%)")
                elif cpu_usage > CONFIG['thresholds']['cpu_warning']:
                    alerts.append(f"Warning: CPU usage {cpu_usage}% (threshold: {CONFIG['thresholds']['cpu_warning']}%)")
                
                # Memory check
                memory_usage = health_data.get('memory', 0)
                if memory_usage > CONFIG['thresholds']['memory_critical']:
                    alerts.append(f"Critical: Memory usage {memory_usage}% (threshold: {CONFIG['thresholds']['memory_critical']}%)")
                elif memory_usage > CONFIG['thresholds']['memory_warning']:
                    alerts.append(f"Warning: Memory usage {memory_usage}% (threshold: {CONFIG['thresholds']['memory_warning']}%)")
                
                # Packet loss check
                packet_loss = ping_result.get('packet_loss', 0)
                if packet_loss > CONFIG['thresholds']['ping_loss_critical']:
                    alerts.append(f"Critical: Packet loss {packet_loss}% (threshold: {CONFIG['thresholds']['ping_loss_critical']}%)")
                elif packet_loss > CONFIG['thresholds']['ping_loss_warning']:
                    alerts.append(f"Warning: Packet loss {packet_loss}% (threshold: {CONFIG['thresholds']['ping_loss_warning']}%)")
                
                health_report['alerts'] = alerts
                
                if alerts:
                    health_report['status'] = 'warning' if any('Warning:' in alert for alert in alerts) else 'critical'
            else:
                health_report['status'] = 'degraded'
        else:
            health_report['status'] = 'unreachable'
        
        return health_report

    def send_alert(self, subject, message):
        """Send email alert"""
        try:
            msg = MimeMultipart()
            msg['From'] = 'network-monitor@university.edu'
            msg['To'] = CONFIG['monitoring']['alert_email']
            msg['Subject'] = subject
            
            msg.attach(MimeText(message, 'plain'))
            
            server = smtplib.SMTP(CONFIG['monitoring']['smtp_server'], CONFIG['monitoring']['smtp_port'])
            server.starttls()
            # In production, use proper SMTP authentication
            text = msg.as_string()
            server.sendmail('network-monitor@university.edu', CONFIG['monitoring']['alert_email'], text)
            server.quit()
            
            logging.info(f"Alert sent: {subject}")
        except Exception as e:
            logging.error(f"Failed to send alert: {str(e)}")

    def generate_report(self, health_reports):
        """Generate comprehensive network health report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_devices': len(health_reports),
                'healthy': 0,
                'warning': 0,
                'critical': 0,
                'unreachable': 0
            },
            'devices': health_reports
        }
        
        # Count device statuses
        for report_item in health_reports:
            status = report_item['status']
            if status == 'healthy':
                report['summary']['healthy'] += 1
            elif status == 'warning':
                report['summary']['warning'] += 1
            elif status == 'critical':
                report['summary']['critical'] += 1
            elif status in ['unreachable', 'degraded']:
                report['summary']['unreachable'] += 1
        
        return report

    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle"""
        logging.info("Starting monitoring cycle")
        
        health_reports = []
        
        for device_name, device_config in CONFIG['devices'].items():
            logging.info(f"Checking device: {device_name}")
            
            health_report = self.check_device_health(device_name, device_config)
            health_reports.append(health_report)
            
            # Track failure counts for alerting
            if health_report['status'] in ['critical', 'unreachable', 'degraded']:
                self.failure_counts[device_name] = self.failure_counts.get(device_name, 0) + 1
                
                # Send alert if threshold reached
                if (self.failure_counts[device_name] >= CONFIG['monitoring']['alert_threshold'] and 
                    device_name not in self.alerts_sent):
                    
                    alert_subject = f"Network Alert: {device_name} - {health_report['status']}"
                    alert_message = f"""
Device: {device_name} ({device_config['ip']})
Status: {health_report['status']}
Consecutive Failures: {self.failure_counts[device_name]}
Timestamp: {health_report['timestamp']}

Checks:
- Ping: {health_report['checks'].get('ping', {}).get('status', 'N/A')}
- SSH: {health_report['checks'].get('ssh', {}).get('status', 'N/A')}

Alerts:
{chr(10).join(health_report.get('alerts', ['No specific alerts']))}

Please investigate immediately.
                    """
                    
                    self.send_alert(alert_subject, alert_message)
                    self.alerts_sent.add(device_name)
            else:
                # Reset failure count on success
                self.failure_counts[device_name] = 0
                if device_name in self.alerts_sent:
                    self.alerts_sent.remove(device_name)
                    # Send recovery notification
                    recovery_subject = f"Network Recovery: {device_name} - Back Online"
                    recovery_message = f"""
Device: {device_name} ({device_config['ip']})
Status: {health_report['status']}
Timestamp: {health_report['timestamp']}

The device has recovered and is now operating normally.
                    """
                    self.send_alert(recovery_subject, recovery_message)
        
        # Generate and save report
        network_report = self.generate_report(health_reports)
        
        # Save report to file
        report_filename = f"network_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(network_report, f, indent=2)
        
        logging.info(f"Monitoring cycle completed. Report saved: {report_filename}")
        
        # Log summary
        summary = network_report['summary']
        logging.info(f"Network Status Summary - Healthy: {summary['healthy']}, Warning: {summary['warning']}, Critical: {summary['critical']}, Unreachable: {summary['unreachable']}")
        
        return network_report

    def continuous_monitoring(self):
        """Run continuous monitoring"""
        logging.info("Starting continuous network monitoring")
        print("Network monitoring started. Press Ctrl+C to stop.")
        
        try:
            while True:
                report = self.run_monitoring_cycle()
                
                # Display summary
                summary = report['summary']
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                      f"Healthy: {summary['healthy']}, Warning: {summary['warning']}, "
                      f"Critical: {summary['critical']}, Unreachable: {summary['unreachable']}")
                
                # Wait for next cycle
                time.sleep(CONFIG['monitoring']['check_interval'])
                
        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user")
            print("\nMonitoring stopped.")

if __name__ == "__main__":
    monitor = NetworkMonitor()
    
    # Run single cycle or continuous monitoring
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        monitor.continuous_monitoring()
    else:
        print("Running single monitoring cycle...")
        report = monitor.run_monitoring_cycle()
        
        # Display results
        print("\n=== Network Health Report ===")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Total Devices: {report['summary']['total_devices']}")
        print(f"Healthy: {report['summary']['healthy']}")
        print(f"Warning: {report['summary']['warning']}")
        print(f"Critical: {report['summary']['critical']}")
        print(f"Unreachable: {report['summary']['unreachable']}")
        
        print("\n=== Device Details ===")
        for device_report in report['devices']:
            print(f"{device_report['device']}: {device_report['status']}")
            if device_report.get('alerts'):
                for alert in device_report['alerts']:
                    print(f"  - {alert}")