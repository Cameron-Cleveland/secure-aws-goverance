#!/bin/bash

echo "🔍 Final pre-push checklist..."

echo ""
echo "1. Checking for sensitive files:"
find . -name "*.pem" -o -name "*.key" -o -name "*.secret" -o -name ".env" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "❌ WARNING: Potential sensitive files found!"
else
    echo "✅ No obvious sensitive files found"
fi

echo ""
echo "2. Checking Terraform state files:"
find . -name "*.tfstate" -o -name "*.tfstate.*" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "❌ WARNING: Terraform state files should not be committed!"
else
    echo "✅ No Terraform state files found"
fi

echo ""
echo "3. Checking .gitignore coverage:"
phases_with_tf=$(find phase-* -name "*.tf" -type f | sed 's|/.*||' | sort -u)
phases_with_gitignore=$(find phase-* -name ".gitignore" -type f | sed 's|/.gitignore||' | sort -u)

echo "Phases with Terraform: $(echo "$phases_with_tf" | wc -l)"
echo "Phases with .gitignore: $(echo "$phases_with_gitignore" | wc -l)"

echo ""
echo "4. Total file count:"
find . -type f | wc -l

echo ""
echo "5. Large files check:"
find . -type f -size +1M 2>/dev/null | while read file; do
    size=$(du -h "$file" | cut -f1)
    echo "⚠️  Large file: $file ($size)"
done

echo ""
echo "✅ Pre-push check complete!"
