#!/bin/bash

echo "🚀 Setting up LLM Knowledge Extractor..."

# Setup Backend
echo "📦 Setting up Python backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env 2>/dev/null || cp .env .env
    echo "⚠️  Please edit backend/.env and add your OpenAI API key"
fi

cd ..

# Setup Frontend
echo "📦 Setting up Vue.js frontend..."
cd frontend

# Install dependencies
npm install

cd ..

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit backend/.env and add your OpenAI API key (optional - it will use mock data without it)"
echo "2. Start the backend: cd backend && source venv/bin/activate && python main.py"
echo "3. In another terminal, start the frontend: cd frontend && npm run serve"
echo "4. Open http://localhost:8080 in your browser"

