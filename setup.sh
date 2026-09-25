#!/bin/bash
# Beam vLLM Setup Script
# Sets up the environment and deploys the vLLM endpoint

echo "🚀 Setting up Beam vLLM deployment..."

# Create virtual environment if it doesn't exist
if [ ! -d "beam-vllm-env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv beam-vllm-env
fi

# Activate virtual environment
source beam-vllm-env/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install beam-client

# Configure Beam with your API token
echo "🔑 Configuring Beam..."
echo "Please run the following command to configure your Beam API token:"
echo "beam configure default --token 1TeToLbg1zL4XKVzkXY_i1gep4VOkdc-zcOxjALAvVveuFf03BueNxPVMhUVM8KdBlT6-ILybZ_q_46GpjSN7w=="
echo ""
echo "Replace YOUR_API_TOKEN_HERE with your actual token from:"
echo "1TeToLbg1zL4XKVzkXY_i1gep4VOkdc-zcOxjALAvVveuFf03BueNxPVMhUVM8KdBlT6-ILybZ_q_46GpjSN7w=="
echo ""

# Test Beam connection
echo "🧪 Testing Beam connection..."
beam apps list

echo ""
echo "✅ Setup complete! Next steps:"
echo "1. Configure your API token (see command above)"
echo "2. Deploy: beam run --gpu A100-40 --memory 16 beam-vllm-setup.py:main"
echo "3. Test: curl https://your-endpoint.app.beam.cloud/"
echo ""
echo "📖 See README.md for detailed instructions and configuration options."
