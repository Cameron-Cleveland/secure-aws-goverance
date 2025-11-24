#!/bin/bash

echo "🔍 Checking for duplicate .gitignore files..."

# Find all .gitignore files
find . -name ".gitignore" -type f | sort > all_gitignores.txt

echo ""
echo "📋 All .gitignore files found:"
cat all_gitignores.txt

echo ""
echo "🔎 Checking for redundant files (both phase and phase/terraform have gitignores):"
while read gitignore; do
    dir=$(dirname "$gitignore")
    parent_dir=$(dirname "$dir")
    parent_gitignore="$parent_dir/.gitignore"
    
    if [[ "$dir" == *"/terraform" ]] && [ -f "$parent_gitignore" ]; then
        echo "⚠️  Potential redundancy:"
        echo "   Parent: $parent_gitignore"
        echo "   Child:  $gitignore"
    fi
done < all_gitignores.txt

echo ""
echo "💡 Recommendation: Keep terraform/ .gitignore files, they're more specific"
rm -f all_gitignores.txt
