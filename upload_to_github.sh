#!/bin/bash

# GitHub Upload Script for Python Cloud DevOps Automation
# This script helps you upload all files to your GitHub repository

echo "🚀 Python Cloud DevOps Automation - GitHub Upload Script"
echo "========================================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Repository URL
REPO_URL="https://github.com/Swagata-ux/python-cloud-devops-automation.git"

echo "📁 Current directory: $(pwd)"
echo "📋 Files to upload:"
ls -la *.py *.md *.log 2>/dev/null || echo "No matching files found"

echo ""
read -p "🤔 Do you want to initialize a new git repository? (y/n): " init_repo

if [[ $init_repo == "y" || $init_repo == "Y" ]]; then
    echo "🔧 Initializing git repository..."
    git init
    
    echo "🔗 Adding remote origin..."
    git remote add origin $REPO_URL
    
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# AWS
.aws/
*.pem

# Logs
*.log
!sample_api.log

# Temporary files
*.tmp
*.temp
EOF

    echo "✅ Git repository initialized!"
fi

echo ""
echo "📦 Adding files to git..."
git add .

echo "💬 Committing files..."
read -p "Enter commit message (or press Enter for default): " commit_msg
if [[ -z "$commit_msg" ]]; then
    commit_msg="Initial commit: Python Cloud DevOps Automation scripts"
fi

git commit -m "$commit_msg"

echo ""
echo "🌐 Pushing to GitHub..."
echo "Note: You may need to authenticate with GitHub"

# Try to push
if git push -u origin main 2>/dev/null; then
    echo "✅ Successfully pushed to main branch!"
elif git push -u origin master 2>/dev/null; then
    echo "✅ Successfully pushed to master branch!"
else
    echo "❌ Push failed. Trying to set upstream branch..."
    git branch -M main
    git push -u origin main
fi

echo ""
echo "🎉 Upload complete!"
echo "🔗 Repository URL: $REPO_URL"
echo ""
echo "📋 Next steps:"
echo "1. Visit your GitHub repository"
echo "2. Verify all files are uploaded"
echo "3. Update repository description and topics"
echo "4. Add collaborators if needed"
echo ""
echo "💡 To update files later, use:"
echo "   git add ."
echo "   git commit -m 'Update: description of changes'"
echo "   git push"