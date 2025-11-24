#!/usr/bin/env python3
import boto3

print("🧪 Testing AWS Connection...")

try:
    # Test EC2 client
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances()
    
    instance_count = 0
    for reservation in response['Reservations']:
        instance_count += len(reservation['Instances'])
    
    print(f"✅ AWS Connection Successful!")
    print(f"📊 Found {instance_count} EC2 instances")
    
except Exception as e:
    print(f"❌ AWS Connection Failed: {e}")
    print("💡 Check your AWS CLI configuration: aws configure")
