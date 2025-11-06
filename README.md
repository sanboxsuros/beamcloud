# Beam vLLM OpenAI-Compatible API

🚀 **Deploy vLLM models on Beam cloud GPUs with an OpenAI-compatible API endpoint**

This setup provides a production-ready LLM deployment with:
- ✅ **OpenAI-compatible API** - Works with existing tools and libraries
- ✅ **Auto-scaling** - Scales from 0 to multiple GPUs
- ✅ **Cost-effective** - Pay-per-use pricing
- ✅ **Zero infrastructure** - No Docker, Kubernetes, or cluster management

## 📊 Current Project Status

### ✅ Completed
- Windows setup script executed successfully
- Virtual environment "beam-vllm-env" created and activated
- beam-client installed and configured
- Beam API token configured and authorized
- PyTorch installed with CUDA support

### 🔄 In Progress
- vLLM installation (pip install vllm currently running)

### ⏳ Next Steps
1. Complete vLLM installation
2. Deploy the endpoint using: `beam run --gpu A100-40 --memory 16000 beam-vllm-setup.py:main`
3. Test the deployed endpoint using: `python test_api.py [ENDPOINT_URL]`

For detailed progress information, see [MEMORY_BANK.md](MEMORY_BANK.md) and [DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md).

## Quick Start

### 1. Setup Environment

#### Windows
```powershell
# Run the Windows setup script
.\setup-windows.ps1

# Activate the virtual environment
.\beam-vllm-env\Scripts\Activate.ps1
```

#### Linux/Mac
```bash
# Make setup script executable
chmod +x setup.sh

# Run setup (creates venv and installs beam-client)
./setup.sh

# Activate the virtual environment
source beam-vllm-env/bin/activate
```

### 2. Configure Beam API

```bash
# Configure your API token (replace with your actual token)
beam configure default --token bq99X2Wzdgo794QrPfWKgzPwFBl7Zog3ajdiUxTgNOWO1daHRnyRB2nB8zqCFKr8KR9VELgSmzpmhesuidmbpQ==
```

### 3. Deploy to Beam

```bash
# Single GPU deployment (recommended for testing)
beam run --gpu A100-40 --memory 16000 beam-vllm-setup.py:main

# Multi-GPU deployment (for larger models)
beam run --gpu A100-40:2 --memory 32000 beam-vllm-setup.py:main
```

### 4. Test Your Endpoint

```bash
# Get your endpoint URL from the deployment output
# Then test with the provided test script:

python test_api.py https://your-pod-id-8888.app.beam.cloud

# Or test with curl:

curl https://your-pod-id-8888.app.beam.cloud/

# Test chat completions
curl -X POST https://your-pod-id-8888.app.beam.cloud/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "microsoft/DialoGPT-medium",
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "max_tokens": 100
  }'
```

## Configuration

### Environment Variables

You can customize the deployment by setting these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_NAME` | `microsoft/DialoGPT-medium` | Hugging Face model name |
| `MAX_MODEL_LEN` | `2048` | Maximum context length |
| `GPU_MEMORY_UTILIZATION` | `0.9` | GPU memory usage (0.0-1.0) |
| `TENSOR_PARALLEL_SIZE` | `1` | Number of GPUs for tensor parallelism |
| `GPU_COUNT` | `1` | Number of GPUs to use |

### Example with Custom Model

```bash
# Deploy with Llama 2 7B
beam run \
  --gpu A100-40:2 \
  --memory 32 \
  --env MODEL_NAME=meta-llama/Llama-2-7b-chat-hf \
  --env TENSOR_PARALLEL_SIZE=2 \
  beam-vllm-setup.py:main
```

## Supported Models

### Small Models (1x A100-40GB)
- microsoft/DialoGPT-medium
- microsoft/DialoGPT-large
- facebook/blenderbot-400M-distill
- google/flan-t5-small
- google/flan-t5-base

### Medium Models (2x A100-40GB)
- microsoft/DialoGPT-xl
- google/flan-t5-large
- meta-llama/Llama-2-7b-chat-hf
- mistralai/Mistral-7B-Instruct-v0.1

### Large Models (4x A100-40GB)
- meta-llama/Llama-2-13b-chat-hf
- mistralai/Mixtral-8x7B-Instruct-v0.1

## API Usage

### OpenAI-Compatible Endpoints

The deployed service provides these OpenAI-compatible endpoints:

#### Chat Completions
```python
import openai

client = openai.OpenAI(
    base_url="https://your-pod-id-8888.app.beam.cloud/v1",
    api_key="dummy"  # Not required for this setup
)

response = client.chat.completions.create(
    model="microsoft/DialoGPT-medium",
    messages=[
        {"role": "user", "content": "Explain quantum computing in simple terms"}
    ],
    max_tokens=200
)

print(response.choices[0].message.content)
```

#### Text Completions
```python
response = client.completions.create(
    model="microsoft/DialoGPT-medium",
    prompt="The future of artificial intelligence is",
    max_tokens=100
)

print(response.choices[0].text)
```

#### Models Endpoint
```python
models = client.models.list()
print(models.data)
```

## Cost Optimization

### Pricing Structure
- **A100-40GB**: ~$1.50-2.00/hour per GPU
- **Memory**: Included in GPU pricing
- **Data Transfer**: Minimal cost for API calls

### Cost-Saving Tips

1. **Use smaller models for testing**
   ```bash
   beam run --gpu A100-40 --env MODEL_NAME=microsoft/DialoGPT-medium
   ```

2. **Set appropriate timeouts**
   ```bash
   beam run --timeout 300  # 5 minutes idle timeout
   ```

3. **Use keep_warm_seconds strategically**
   - 0 seconds = Cold start (slower first request)
   - 300-600 seconds = Good balance for production

### Cost Estimation
- **Development/Testing**: $0.10-0.50/day
- **Light Production**: $5-15/day
- **Heavy Production**: $20-100/day

## Monitoring and Logs

### View Logs
```bash
beam logs --pod your-pod-id
```

### Monitor Usage
```bash
beam usage
```

### Check Status
```bash
beam pods list
```

## Troubleshooting

### Common Issues

1. **Out of Memory Error**
   ```bash
   # Reduce memory utilization or use smaller model
   beam run --gpu A100-40 --env GPU_MEMORY_UTILIZATION=0.7
   ```

2. **Cold Start Delays**
   ```bash
   # Increase keep_warm for faster responses
   beam run --keep_warm_seconds 300
   ```

3. **Model Download Fails**
   ```bash
   # Ensure model is available on Hugging Face
   beam run --gpu A100-40 --env MODEL_NAME=valid/huggingface/model
   ```

4. **API Timeout**
   ```bash
   # Increase timeout for complex queries
   beam run --timeout 600
   ```

### Performance Optimization

1. **Model Choice**
   - Use `microsoft/DialoGPT-medium` for fast responses
   - Use larger models only when needed

2. **Batching**
   - vLLM automatically handles request batching
   - Monitor throughput with `beam metrics`

3. **GPU Selection**
   - A100-40GB is most cost-effective for most models
   - Use A100-80GB only for very large models

## Advanced Configuration

### Custom Model Loading
```python
# Modify beam-vllm-setup.py to add custom models
CUSTOM_MODELS = {
    "my-model": "path/to/my/model",
    "fine-tuned": "username/my-fine-tuned-model"
}
```

### Multi-Model Setup
```bash
# Deploy multiple models on different ports
beam run --gpu A100-40:2 \
  --port 8000 \
  --env MODEL_NAME=model1 \
  beam-vllm-setup.py:main

beam run --gpu A100-40:2 \
  --port 8001 \
  --env MODEL_NAME=model2 \
  beam-vllm-setup.py:main
```

## Security Considerations

1. **API Keys**: This setup doesn't require authentication (public endpoint)
2. **Rate Limiting**: Implement rate limiting in production
3. **Input Validation**: Add input sanitization for production use
4. **HTTPS**: All Beam endpoints are HTTPS by default

## Next Steps

1. **Test locally first** to ensure your model works
2. **Start with small models** to understand the workflow
3. **Monitor costs** and optimize as needed
4. **Scale up** to larger models when ready
5. **Add authentication** for production use

## Support

- [Beam Documentation](https://docs.beam.cloud/)
- [vLLM Documentation](https://docs.vllm.ai/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [MEMORY_BANK.md](MEMORY_BANK.md) - Detailed project progress and technical notes
- [DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md) - Current deployment status and specifications

---

**Happy LLM hosting! 🎉**