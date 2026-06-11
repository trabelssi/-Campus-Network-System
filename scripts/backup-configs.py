#!/usr/bin/env python3
"""
Network Configuration Backup Script
Author: Trabelsi Mohamed Amine  
Academic Project: Master's Degree - Network Engineering
Description: Automated backup of network device configurations for Secure Campus Network System
Version: 1.0.0
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
import paramiko
import schedule
import argparse
from pathlib import Path

# Configuration
CONFIG = {
    'devices': {
        'HQ-CORE-SW01': {
            'ip': '172.16.10.2',
            'type': 'ios',
            'username': 'admin',
            'password': 'Admin123!',  # Use secure credential management in production
            'enable_password': 'Enable789!',
            'backup_commands': [
                'show running-config',
                'show startup-config', 
                'show version',
                'show vlan brief',
                'show ip route',
                'show spanning-tree summary'
            ]
        },
        'HQ-CORE-SW02': {
            'ip': '172.16.10.3',
            'type': 'ios',
            'username': 'admin',
            'password': 'Admin123!',
            'enable_password': 'Enable789!',
            'backup_commands': [
                'show running-config',
                'show startup-config',
                'show version',
                'show vlan brief',
                'show ip route',
                'show spanning-tree summary'
            ]
        },
        'HQ-ASA-FW01': {
            'ip': '172.16.10.4',
            'type': 'asa',
            'username': 'admin',
            'password': 'Admin123!',
            'enable_password': 'Enable789!',
            'backup_commands': [
                'show running-config',
                'show startup-config',
                'show version',
                'show interface ip brief',
                'show route',
                'show crypto isakmp sa',
                'show crypto ipsec sa',
                'show access-list',
                'show nat'
            ]
        },
        'HQ-WLC-01': {
            'ip': '172.16.10.5',
            'type': 'wlc',
            'username': 'admin',
            'password': 'Admin123!',
            'backup_commands': [
                'show sysinfo',
                'show interface summary',
                'show wlan summary',
                'show ap summary',
                'show security summary'
            ]
        },
        'BR-CORE-SW01': {
            'ip': '172.16.11.2',
            'type': 'ios',
            'username': 'admin',
            'password': 'Admin123!',
            'enable_password': 'Enable789!',
            'backup_commands': [
                'show running-config',
                'show startup-config',
                'show version',
                'show vlan brief',
                'show ip route'
            ]
        },
        'BR-CORE-SW02': {
            'ip': '172.16.11.3',
            'type': 'ios',
            'username': 'admin',
            'password': 'Admin123!',
            'enable_password': 'Enable789!',
            'backup_commands': [
                'show running-config',
                'show startup-config',
                'show version',
                'show vlan brief',
                'show ip route'
            ]
        },
        'BR-ASA-FW01': {
            'ip': '172.16.11.4',
            'type': 'asa',
            'username': 'admin',
            'password': 'Admin123!',
            'enable_password': 'Enable789!',
            'backup_commands': [
                'show running-config',
                'show startup-config',
                'show version',
                'show interface ip brief',
                'show route',
                'show crypto isakmp sa',
                'show crypto ipsec sa'
            ]
        }
    },
    'backup_settings': {
        'backup_directory': 'config_backups',
        'retention_days': 30,
        'compression': True,
        'ssh_timeout': 30,
        'command_timeout': 60,
        'log_file': 'backup.log',
        'notification_email': 'network-admin@university.edu'
    }
}

# Setup logging
logging.basicConfig(
    filename=CONFIG['backup_settings']['log_file'],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class NetworkBackup:
    def __init__(self):
        self.backup_dir = Path(CONFIG['backup_settings']['backup_directory'])
        self.backup_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different backup types
        (self.backup_dir / 'daily').mkdir(exist_ok=True)
        (self.backup_dir / 'weekly').mkdir(exist_ok=True)
        (self.backup_dir / 'monthly').mkdir(exist_ok=True)
        
        self.backup_stats = {
            'successful': 0,
            'failed': 0,
            'total_devices': 0,
            'start_time': None,
            'end_time': None
        }

    def connect_device(self, device_name, device_config):
        """Establish SSH connection to network device"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(
                hostname=device_config['ip'],
                username=device_config['username'],
                password=device_config['password'],
                timeout=CONFIG['backup_settings']['ssh_timeout']
            )
            
            return ssh
        except Exception as e:
            logging.error(f"Failed to connect to {device_name}: {str(e)}")
            raise

    def execute_commands(self, ssh, device_config, commands):
        """Execute commands on connected device"""
        results = {}
        
        try:
            # For IOS devices, enter enable mode
            if device_config['type'] in ['ios']:
                channel = ssh.invoke_shell()
                channel.send('enable\n')
                time.sleep(1)
                channel.send(f"{device_config['enable_password']}\n")
                time.sleep(1)
                channel.send('terminal length 0\n')  # Disable paging
                time.sleep(1)
                
                for command in commands:
                    logging.info(f"Executing command: {command}")
                    channel.send(f"{command}\n")
                    time.sleep(2)  # Wait for command to complete
                    
                    output = ""
                    while channel.recv_ready():
                        output += channel.recv(4096).decode('utf-8')
                    
                    # Clean up output
                    output = self.clean_output(output, command)
                    results[command] = output
                
                channel.close()
                
            elif device_config['type'] == 'asa':
                # ASA commands
                for command in commands:
                    logging.info(f"Executing ASA command: {command}")
                    stdin, stdout, stderr = ssh.exec_command(
                        command, 
                        timeout=CONFIG['backup_settings']['command_timeout']
                    )
                    
                    output = stdout.read().decode('utf-8')
                    error = stderr.read().decode('utf-8')
                    
                    if error:
                        logging.warning(f"Command '{command}' produced error: {error}")
                    
                    results[command] = output
                    
            elif device_config['type'] == 'wlc':
                # WLC commands (might need different handling)
                for command in commands:
                    logging.info(f"Executing WLC command: {command}")
                    stdin, stdout, stderr = ssh.exec_command(
                        command,
                        timeout=CONFIG['backup_settings']['command_timeout']
                    )
                    
                    output = stdout.read().decode('utf-8')
                    results[command] = output
            
        except Exception as e:
            logging.error(f"Error executing commands: {str(e)}")
            raise
        
        return results

    def clean_output(self, output, command):
        """Clean command output by removing prompts and unnecessary text"""
        lines = output.split('\n')
        cleaned_lines = []
        
        skip_patterns = [
            'terminal length 0',
            'enable',
            '--More--',
            'Building configuration'
        ]
        
        for line in lines:
            # Skip lines containing command echo or prompts
            if any(pattern in line for pattern in skip_patterns):
                continue
            
            # Remove ANSI escape codes
            import re
            line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            
            # Remove carriage returns
            line = line.replace('\r', '')
            
            if line.strip():
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def backup_device(self, device_name, device_config):
        """Backup a single network device"""
        logging.info(f"Starting backup for {device_name}")
        
        try:
            # Connect to device
            ssh = self.connect_device(device_name, device_config)
            
            # Execute backup commands
            command_results = self.execute_commands(ssh, device_config, device_config['backup_commands'])
            
            # Close SSH connection
            ssh.close()
            
            # Save backup files
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            device_backup_dir = self.backup_dir / 'daily' / device_name
            device_backup_dir.mkdir(exist_ok=True)
            
            backup_info = {
                'device_name': device_name,
                'device_ip': device_config['ip'],
                'device_type': device_config['type'],
                'backup_timestamp': timestamp,
                'backup_date': datetime.now().isoformat(),
                'commands_executed': list(command_results.keys()),
                'backup_status': 'successful'
            }
            
            # Save each command output to separate file
            for command, output in command_results.items():
                # Clean command name for filename
                safe_command = command.replace(' ', '_').replace('/', '_')
                filename = f"{device_name}_{safe_command}_{timestamp}.txt"
                filepath = device_backup_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# Device: {device_name}\n")
                    f.write(f"# IP Address: {device_config['ip']}\n")
                    f.write(f"# Command: {command}\n")
                    f.write(f"# Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"# Backup Script Version: 1.0.0\n")
                    f.write("#" + "="*50 + "\n\n")
                    f.write(output)
                
                logging.info(f"Saved {command} output to {filepath}")
            
            # Save backup metadata
            metadata_file = device_backup_dir / f"{device_name}_backup_info_{timestamp}.json"
            with open(metadata_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            # Create running-config specific backup (most important)
            if 'show running-config' in command_results:
                config_backup_dir = self.backup_dir / 'configs'
                config_backup_dir.mkdir(exist_ok=True)
                
                config_filename = f"{device_name}_running-config_{timestamp}.txt"
                config_filepath = config_backup_dir / config_filename
                
                with open(config_filepath, 'w', encoding='utf-8') as f:
                    f.write(command_results['show running-config'])
                
                logging.info(f"Saved running configuration to {config_filepath}")
            
            logging.info(f"Successfully backed up {device_name}")
            self.backup_stats['successful'] += 1
            return True
            
        except Exception as e:
            logging.error(f"Failed to backup {device_name}: {str(e)}")
            self.backup_stats['failed'] += 1
            
            # Create error report
            error_report = {
                'device_name': device_name,
                'error_timestamp': datetime.now().isoformat(),
                'error_message': str(e),
                'backup_status': 'failed'
            }
            
            error_dir = self.backup_dir / 'errors'
            error_dir.mkdir(exist_ok=True)
            
            error_file = error_dir / f"{device_name}_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(error_file, 'w') as f:
                json.dump(error_report, f, indent=2)
            
            return False

    def backup_all_devices(self):
        """Backup all configured network devices"""
        logging.info("Starting backup process for all devices")
        self.backup_stats['start_time'] = datetime.now()
        self.backup_stats['total_devices'] = len(CONFIG['devices'])
        
        print(f"Starting backup of {self.backup_stats['total_devices']} devices...")
        
        for device_name, device_config in CONFIG['devices'].items():
            print(f"Backing up {device_name}...", end=' ')
            
            success = self.backup_device(device_name, device_config)
            
            if success:
                print("✅ Success")
            else:
                print("❌ Failed")
        
        self.backup_stats['end_time'] = datetime.now()
        duration = self.backup_stats['end_time'] - self.backup_stats['start_time']
        
        # Generate backup report
        self.generate_backup_report(duration)
        
        # Cleanup old backups
        self.cleanup_old_backups()
        
        logging.info(f"Backup process completed. Success: {self.backup_stats['successful']}, Failed: {self.backup_stats['failed']}")

    def generate_backup_report(self, duration):
        """Generate backup completion report"""
        report = {
            'backup_summary': {
                'total_devices': self.backup_stats['total_devices'],
                'successful_backups': self.backup_stats['successful'],
                'failed_backups': self.backup_stats['failed'],
                'success_rate': round((self.backup_stats['successful'] / self.backup_stats['total_devices']) * 100, 2),
                'start_time': self.backup_stats['start_time'].isoformat(),
                'end_time': self.backup_stats['end_time'].isoformat(),
                'duration_seconds': duration.total_seconds(),
                'backup_directory': str(self.backup_dir)
            },
            'device_details': []
        }
        
        # Add device-specific details
        for device_name in CONFIG['devices'].keys():
            device_status = 'successful' if device_name in [d for d in CONFIG['devices'].keys() if self.backup_stats['successful'] > 0] else 'failed'
            report['device_details'].append({
                'device_name': device_name,
                'status': device_status,
                'ip_address': CONFIG['devices'][device_name]['ip']
            })
        
        # Save report
        report_filename = f"backup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.backup_dir / report_filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logging.info(f"Backup report saved: {report_path}")
        
        # Print summary
        print(f"\n=== Backup Summary ===")
        print(f"Total Devices: {report['backup_summary']['total_devices']}")
        print(f"Successful: {report['backup_summary']['successful_backups']}")
        print(f"Failed: {report['backup_summary']['failed_backups']}")
        print(f"Success Rate: {report['backup_summary']['success_rate']}%")
        print(f"Duration: {report['backup_summary']['duration_seconds']:.1f} seconds")

    def cleanup_old_backups(self):
        """Remove backup files older than retention period"""
        retention_days = CONFIG['backup_settings']['retention_days']
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        logging.info(f"Cleaning up backups older than {retention_days} days")
        
        cleaned_count = 0
        
        for backup_type in ['daily', 'weekly', 'monthly']:
            backup_type_dir = self.backup_dir / backup_type
            
            if backup_type_dir.exists():
                for device_dir in backup_type_dir.iterdir():
                    if device_dir.is_dir():
                        for backup_file in device_dir.iterdir():
                            # Check file modification time
                            file_modified = datetime.fromtimestamp(backup_file.stat().st_mtime)
                            
                            if file_modified < cutoff_date:
                                try:
                                    backup_file.unlink()
                                    cleaned_count += 1
                                    logging.info(f"Deleted old backup: {backup_file}")
                                except Exception as e:
                                    logging.error(f"Failed to delete {backup_file}: {str(e)}")
        
        logging.info(f"Cleanup completed. Removed {cleaned_count} old backup files")

    def create_weekly_backup(self):
        """Create weekly backup (copy of latest daily backup)"""
        logging.info("Creating weekly backup")
        
        weekly_dir = self.backup_dir / 'weekly'
        daily_dir = self.backup_dir / 'daily'
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        for device_name in CONFIG['devices'].keys():
            device_daily_dir = daily_dir / device_name
            device_weekly_dir = weekly_dir / device_name
            device_weekly_dir.mkdir(exist_ok=True)
            
            if device_daily_dir.exists():
                # Find latest backup
                latest_config = None
                latest_time = datetime.min
                
                for config_file in device_daily_dir.glob(f"{device_name}_show_running-config_*.txt"):
                    file_time = datetime.fromtimestamp(config_file.stat().st_mtime)
                    if file_time > latest_time:
                        latest_time = file_time
                        latest_config = config_file
                
                if latest_config:
                    # Copy to weekly backup
                    weekly_config = device_weekly_dir / f"{device_name}_weekly_backup_{timestamp}.txt"
                    weekly_config.write_text(latest_config.read_text())
                    logging.info(f"Created weekly backup: {weekly_config}")

    def create_monthly_backup(self):
        """Create monthly backup (copy of latest weekly backup)"""
        logging.info("Creating monthly backup")
        
        monthly_dir = self.backup_dir / 'monthly'
        weekly_dir = self.backup_dir / 'weekly'
        
        timestamp = datetime.now().strftime('%Y%m')
        
        for device_name in CONFIG['devices'].keys():
            device_weekly_dir = weekly_dir / device_name
            device_monthly_dir = monthly_dir / device_name
            device_monthly_dir.mkdir(exist_ok=True)
            
            if device_weekly_dir.exists():
                # Find latest weekly backup
                latest_backup = None
                latest_time = datetime.min
                
                for backup_file in device_weekly_dir.glob(f"{device_name}_weekly_backup_*.txt"):
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if file_time > latest_time:
                        latest_time = file_time
                        latest_backup = backup_file
                
                if latest_backup:
                    # Copy to monthly backup
                    monthly_backup = device_monthly_dir / f"{device_name}_monthly_backup_{timestamp}.txt"
                    monthly_backup.write_text(latest_backup.read_text())
                    logging.info(f"Created monthly backup: {monthly_backup}")

def schedule_backups():
    """Schedule automated backups"""
    backup_system = NetworkBackup()
    
    # Schedule daily backups at 2 AM
    schedule.every().day.at("02:00").do(backup_system.backup_all_devices)
    
    # Schedule weekly backups on Sundays at 3 AM
    schedule.every().sunday.at("03:00").do(backup_system.create_weekly_backup)
    
    # Schedule monthly backups on the 1st of each month at 4 AM
    schedule.every().day.at("04:00").do(backup_system.create_monthly_backup)
    
    print("Backup scheduler started. Running continuously...")
    print("Daily backups: 2:00 AM")
    print("Weekly backups: Sundays 3:00 AM")
    print("Monthly backups: 1st of month 4:00 AM")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nScheduler stopped.")
        logging.info("Backup scheduler stopped by user")

def main():
    parser = argparse.ArgumentParser(description='Network Configuration Backup Tool')
    parser.add_argument('--schedule', action='store_true', help='Run in scheduled mode')
    parser.add_argument('--device', help='Backup specific device only')
    parser.add_argument('--weekly', action='store_true', help='Create weekly backup')
    parser.add_argument('--monthly', action='store_true', help='Create monthly backup')
    parser.add_argument('--cleanup', action='store_true', help='Run cleanup only')
    
    args = parser.parse_args()
    
    backup_system = NetworkBackup()
    
    if args.schedule:
        schedule_backups()
    elif args.device:
        if args.device in CONFIG['devices']:
            print(f"Backing up {args.device}...")
            success = backup_system.backup_device(args.device, CONFIG['devices'][args.device])
            if success:
                print(f"✅ Successfully backed up {args.device}")
            else:
                print(f"❌ Failed to backup {args.device}")
        else:
            print(f"Error: Device '{args.device}' not found in configuration")
            print(f"Available devices: {list(CONFIG['devices'].keys())}")
    elif args.weekly:
        backup_system.create_weekly_backup()
    elif args.monthly:
        backup_system.create_monthly_backup()
    elif args.cleanup:
        backup_system.cleanup_old_backups()
    else:
        backup_system.backup_all_devices()

if __name__ == "__main__":
    main()