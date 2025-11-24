#!/bin/bash

echo "🔧 Adding .gitignore files to specific phases..."

# Gitignore content
GITIGNORE_CONTENT='# Terraform
*.tfstate
*.tfstate.*
.terraform/
*.tfvars
.terraform.lock.hcl
terraform.tfstate.backup

# AWS credentials
*.pem
*.key
*.secret
.env
.aws/

# OS files
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp

# Backup files
*.backup
backup/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Python
__pycache__/
*.py[cod]
*$py.class

# Lambda packages (keep source, ignore generated)
*.zip
!src/ai-scripts/*.zip'

# List of phases to target
PHASES=(
    "phase-1-governance"
    "phase-2-security-automation" 
    "phase-3-data-processing"
    "phase-5-containerization"
    "phase-6-serverless"
    "phase-7-iam-identity-center"
    "phase-8-data-governance"
    "phase-9-lza-implementation"
    "phase-10-ai-ml-governance"
)

for phase in "${PHASES[@]}"; do
    if [ -d "$phase" ]; then
        gitignore_path="$phase/.gitignore"
        if [ ! -f "$gitignore_path" ]; then
            echo "$GITIGNORE_CONTENT" > "$gitignore_path"
            echo "✅ Created: $gitignore_path"
            
            # Also add to terraform subdirectory if it exists
            if [ -d "$phase/terraform" ]; then
                tf_gitignore="$phase/terraform/.gitignore"
                echo "$GITIGNORE_CONTENT" > "$tf_gitignore"
                echo "✅ Created: $tf_gitignore"
            fi
        else
            echo "⚠️  Already exists: $gitignore_path"
        fi
    else
        echo "❌ Directory not found: $phase"
    fi
done

echo ""
echo "📋 Summary of created gitignore files:"
find . -name ".gitignore" -type f | sort
