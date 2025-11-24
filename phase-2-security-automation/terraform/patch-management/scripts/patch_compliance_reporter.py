#!/usr/bin/env python3
import boto3
import json
from datetime import datetime

def generate_patch_compliance_report():
    ec2 = boto3.client('ec2')
    ssm = boto3.client('ssm')
    
    print("🔄 Generating Patch Compliance Report...")
    
    # Get all instances
    instances = ec2.describe_instances()
    report_data = []
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            if instance['State']['Name'] == 'running':
                instance_id = instance['InstanceId']
                instance_name = "Unnamed"
                
                # Get instance name from tags
                for tag in instance.get('Tags', []):
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                        break
                
                # Check SSM management
                try:
                    ssm_info = ssm.describe_instance_information(
                        Filters=[{'Key': 'InstanceIds', 'Values': [instance_id]}]
                    )
                    ssm_managed = len(ssm_info['InstanceInformationList']) > 0
                except:
                    ssm_managed = False
                
                # Get patch compliance
                if ssm_managed:
                    try:
                        patches = ssm.describe_instance_patches(InstanceId=instance_id)
                        missing_patches = len([p for p in patches.get('Patches', []) 
                                             if p.get('State') in ['Missing', 'Failed']])
                        compliance_status = "COMPLIANT" if missing_patches == 0 else "NON_COMPLIANT"
                    except:
                        missing_patches = "Unknown"
                        compliance_status = "UNKNOWN"
                else:
                    missing_patches = "N/A"
                    compliance_status = "NOT_MANAGED"
                
                report_data.append({
                    'InstanceId': instance_id,
                    'InstanceName': instance_name,
                    'SSMManaged': ssm_managed,
                    'MissingPatches': missing_patches,
                    'ComplianceStatus': compliance_status,
                    'LastChecked': datetime.now().isoformat()
                })
    
    # Print report
    print("\n" + "="*80)
    print("📊 PATCH COMPLIANCE REPORT")
    print("="*80)
    print(f"{'Instance Name':<30} {'Instance ID':<20} {'SSM Managed':<12} {'Missing Patches':<16} {'Status':<15}")
    print("-"*80)
    
    for instance in report_data:
        print(f"{instance['InstanceName']:<30} {instance['InstanceId']:<20} "
              f"{'Yes' if instance['SSMManaged'] else 'No':<12} "
              f"{instance['MissingPatches']:<16} {instance['ComplianceStatus']:<15}")
    
    print("="*80)
    
    # Summary
    total_instances = len(report_data)
    compliant_instances = len([i for i in report_data if i['ComplianceStatus'] == 'COMPLIANT'])
    managed_instances = len([i for i in report_data if i['SSMManaged']])
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total Instances: {total_instances}")
    print(f"   SSM Managed: {managed_instances}")
    print(f"   Compliant: {compliant_instances}")
    print(f"   Compliance Rate: {(compliant_instances/total_instances*100 if total_instances > 0 else 0):.1f}%")

if __name__ == "__main__":
    generate_patch_compliance_report()
