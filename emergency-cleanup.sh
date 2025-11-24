#!/bin/bash

echo "🚨 EMERGENCY CLEANUP - Removing sensitive files before GitHub push"

echo ""
echo "1. REMOVING TERRAFORM STATE FILES..."
find . -name "*.tfstate" -o -name "*.tfstate.*" -o -name "terraform.tfstate.backup*" | while read file; do
    echo "🗑️  Removing: $file"
    rm -f "$file"
done

echo ""
echo "2. REMOVING TERRAFORM PROVIDER BINARIES..."
find . -name ".terraform" -type d | while read dir; do
    echo "🗑️  Removing: $dir"
    rm -rf "$dir"
done

echo ""
echo "3. REMOVING ANY REMAINING SENSITIVE FILES..."
find . -name "*.pem" -o -name "*.key" -o -name "*.secret" -o -name ".env" 2>/dev/null | while read file; do
    echo "🗑️  Removing: $file"
    rm -f "$file"
done

echo ""
echo "4. VERIFYING CLEANUP..."
echo "Remaining state files:"
find . -name "*.tfstate" -o -name "*.tfstate.*" 2>/dev/null | wc -l

echo "Remaining .terraform directories:"
find . -name ".terraform" -type d 2>/dev/null | wc -l

echo ""
echo "✅ Emergency cleanup complete!"
