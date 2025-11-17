
```bash
#!/bin/bash
# Automated setup script for AgentOS

echo "🚀 Setting up AgentOS..."

# Create directory structure
echo "📁 Creating directories..."
mkdir -p src/agentos/{core,llm,memory,tools,utils}
mkdir -p config
mkdir -p data/{memory/conversations,memory/embeddings,logs}
mkdir -p tests/{unit,integration}
mkdir -p docs/examples

# Create __init__.py files
echo "📝 Creating __init__.py files..."
touch src/agentos/__init__.py
touch src/agentos/core/__init__.py
touch src/agentos/llm/__init__.py
touch src/agentos/memory/__init__.py
touch src/agentos/tools/__init__.py
touch src/agentos/utils/__init__.py
touch config/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py

echo "✅ Directory structure created!"

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Activate based on OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install in development mode
echo "🔧 Installing AgentOS in development mode..."
pip install -e .

# Create .gitignore
echo "📄 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data
data/memory/*.db
data/logs/*.log
.agentos_history

# Distribution
build/
dist/
*.egg-info/

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
EOF

echo "✅ Setup complete!"
echo ""
echo "🎉 AgentOS is ready!"
echo ""
echo "To start using AgentOS:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate  # Linux/Mac"
echo "     venv\\Scripts\\activate    # Windows"
echo ""
echo "  2. Run AgentOS:"
echo "     agentos"
echo ""
echo "  3. Or run tests:"
echo "     pytest tests/ -v"
```

## File 40: setup_project.bat (Windows Setup Script)

```batch
@echo off
echo Setting up AgentOS...

:: Create directories
echo Creating directories...
mkdir src\agentos\core 2>nul
mkdir src\agentos\llm 2>nul
mkdir src\agentos\memory 2>nul
mkdir src\agentos\tools 2>nul
mkdir src\agentos\utils 2>nul
mkdir config 2>nul
mkdir data\memory\conversations 2>nul
mkdir data\memory\embeddings 2>nul
mkdir data\logs 2>nul
mkdir tests\unit 2>nul
mkdir tests\integration 2>nul

:: Create __init__.py files
echo Creating __init__.py files...
type nul > src\agentos\__init__.py
type nul > src\agentos\core\__init__.py
type nul > src\agentos\llm\__init__.py
type nul > src\agentos\memory\__init__.py
type nul > src\agentos\tools\__init__.py
type nul > src\agentos\utils\__init__.py
type nul > config\__init__.py
type nul > tests\__init__.py

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv

:: Activate and install
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo Installing AgentOS...
pip install -e .

echo.
echo Setup complete!
echo.
echo To start using AgentOS:
echo   1. Activate: venv\Scripts\activate
echo   2. Run: agentos
echo.
pause
```