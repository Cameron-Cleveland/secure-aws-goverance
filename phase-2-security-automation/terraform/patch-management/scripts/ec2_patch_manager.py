#!/usr/bin/env python3
"""
Ultra Simple EC2 Patch Management Script
Handles scanning and patching EC2 instances with SSM
"""

import boto3
import json
from datetime import datetime, timedelta

class EC2PatchManager:
    def __init__(self):
        """Initialize AWS clients"""
        self.ec2 = boto3.client('ec2')
        self.ssm = boto3.client('ssm')
        
    def get_all_instances(self):
        """Get all EC2 instances in the region"""
        try:
            response = self.ec2.describe_instances()
            instances = []
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    # Only include running instances
                    if instance['State']['Name'] == 'running':
                        instances.append(instance)
            
            print(f"📊 Found {len(instances)} running EC2 instances")
            return instances
            
        except Exception as e:
            print(f"❌ Error getting instances: {e}")
            return []
    
    def is_instance_managed_by_ssm(self, instance_id):
        """Check if instance can be managed by SSM"""
        try:
            response = self.ssm.describe_instance_information(
                Filters=[
                    {
                        'Key': 'InstanceIds',
                        'Values': [instance_id]
                    }
                ]
            )
            return len(response['InstanceInformationList']) > 0
        except Exception as e:
            print(f"❌ Error checking SSM management for {instance_id}: {e}")
            return False
    
    def scan_instance_patches(self, instance_id):
        """Scan instance for missing patches"""
        try:
            print(f"🔍 Scanning patches for instance: {instance_id}")
            
            response = self.ssm.describe_instance_patches(
                InstanceId=instance_id
            )
            
            # Count missing patches
            missing_patches = []
            for patch in response.get('Patches', []):
                if patch.get('State') in ['Missing', 'Failed']:
                    missing_patches.append(patch)
            
            print(f"📦 Instance {instance_id} has {len(missing_patches)} missing patches")
            return missing_patches
            
        except Exception as e:
            print(f"❌ Error scanning patches for {instance_id}: {e}")
            return []
    
    def install_missing_patches(self, instance_id):
        """Install missing patches on instance"""
        try:
            print(f"🚀 Installing patches on instance: {instance_id}")
            
            response = self.ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName='AWS-RunPatchBaseline',
                Parameters={
                    'Operation': ['Install']
                },
                TimeoutSeconds=600
            )
            
            command_id = response['Command']['CommandId']
            print(f"✅ Patch installation started for {instance_id}, Command ID: {command_id}")
            return command_id
            
        except Exception as e:
            print(f"❌ Error installing patches on {instance_id}: {e}")
            return None
    
    def generate_patch_report(self, instances):
        """Generate a simple patch compliance report"""
        print("\n" + "="*50)
        print("📋 PATCH MANAGEMENT REPORT")
        print("="*50)
        
        for instance in instances:
            instance_id = instance['InstanceId']
            instance_name = "Unnamed"
            
            # Try to get instance name from tags
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break
            
            print(f"\nInstance: {instance_name} ({instance_id})")
            
            # Check SSM management
            if self.is_instance_managed_by_ssm(instance_id):
                patches = self.scan_instance_patches(instance_id)
                status = "🟢 Compliant" if len(patches) == 0 else "🟡 Needs Patching"
                print(f"  Status: {status}")
                print(f"  Missing Patches: {len(patches)}")
            else:
                print(f"  Status: 🔴 Not managed by SSM")
        
        print("\n" + "="*50)

def main():
    """Main function"""
    print("🚀 Starting EC2 Patch Management...")
    
    # Create patch manager
    patch_manager = EC2PatchManager()
    
    # Get all instances
    instances = patch_manager.get_all_instances()
    
    if not instances:
        print("❌ No running EC2 instances found")
        return
    
    # Generate report
    patch_manager.generate_patch_report(instances)
    
    # Ask user if they want to install patches
    choice = input("\n❓ Do you want to install missing patches? (yes/no): ").lower().strip()
    
    if choice in ['yes', 'y']:
        for instance in instances:
            instance_id = instance['InstanceId']
            if patch_manager.is_instance_managed_by_ssm(instance_id):
                patch_manager.install_missing_patches(instance_id)
            else:
                print(f"⚠️  Skipping {instance_id} - not managed by SSM")
        
        print("\n✅ Patch installation commands sent!")
        print("💡 Check AWS Systems Manager → Run Command for status")
    else:
        print("ℹ️  Patch installation skipped")

if __name__ == "__main__":
    main()
