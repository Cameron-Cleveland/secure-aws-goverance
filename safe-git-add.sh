#!/bin/bash

echo "🔒 Safe Git Add - Only adding non-sensitive files"

# First, remove any accidentally added sensitive files
git rm --cached -r .terraform 2>/dev/null
git rm --cached *.tfstate 2>/dev/null
git rm --cached *.tfstate.* 2>/dev/null
git rm --cached *.pem 2>/dev/null
git rm --cached *.key 2>/dev/null

# Add all files (gitignore will prevent sensitive ones)
git add .

echo ""
echo "📋 Files that WILL be committed:"
git status --short

echo ""
echo "⚠️  Files that WON'T be committed (protected by .gitignore):"
git status --ignored --short | head -20

echo ""
read -p "Continue with commit? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Commit cancelled"
    exit 1
fi
