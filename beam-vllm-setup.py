#!/usr/bin/env python3
"""
Beam vLLM Deployment Script
Creates an OpenAI-compatible API using vLLM on Beam cloud GPUs
"""

from beam import endpoint
import os
import logging
from typing import Dict, Any, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import vllm
import torch
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "microsoft/DialoGPT-medium")
MAX_MODEL_LEN = int(os.getenv("MAX_MODEL_LEN", "2048"))
GPU_MEMORY_UTILIZATION = float(os.getenv("GPU_MEMORY_UTILIZATION", "0.9"))
TENSOR_PARALLEL_SIZE = int(os.getenv("TENSOR_PARALLEL_SIZE", "1"))
GPU_COUNT = int(os.getenv("GPU_COUNT", "1"))

# FastAPI app
app = FastAPI(title="vLLM OpenAI-Compatible API", version="1.0.0")

# Request/Response models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    stream: Optional[bool] = False

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Dict[str, int]

class CompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    stream: Optional[bool] = False

class CompletionChoice(BaseModel):
    text: str
    index: int
    finish_reason: str

class CompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: Dict[str, int]

# Global vLLM engine
llm = None

def initialize_model():
    """Initialize the vLLM model"""
    global llm
    
    try:
        logger.info(f"Initializing vLLM model: {MODEL_NAME}")
        logger.info(f"GPU Count: {GPU_COUNT}")
        logger.info(f"Tensor Parallel Size: {TENSOR_PARALLEL_SIZE}")
        logger.info(f"Max Model Length: {MAX_MODEL_LEN}")
        logger.info(f"GPU Memory Utilization: {GPU_MEMORY_UTILIZATION}")
        
        # Initialize vLLM engine
        llm = vllm.LLM(
            model=MODEL_NAME,
            tensor_parallel_size=TENSOR_PARALLEL_SIZE,
            gpu_memory_utilization=GPU_MEMORY_UTILIZATION,
            max_model_len=MAX_MODEL_LEN,
            trust_remote_code=True,
            dtype="auto"
        )
        
        logger.info("vLLM model initialized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize vLLM model: {str(e)}")
        return False

def format_openai_prompt(messages: List[ChatMessage]) -> str:
    """Convert OpenAI-style messages to a single prompt string"""
    formatted_messages = []
    
    for message in messages:
        role = message.role.lower()
        content = message.content
        
        if role == "system":
            formatted_messages.append(f"System: {content}")
        elif role == "user":
            formatted_messages.append(f"Human: {content}")
        elif role == "assistant":
            formatted_messages.append(f"Assistant: {content}")
    
    # Add assistant prefix for completion
    formatted_messages.append("Assistant:")
    
    return "\n".join(formatted_messages)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "timestamp": datetime.now().isoformat(),
        "gpu_count": GPU_COUNT,
        "tensor_parallel_size": TENSOR_PARALLEL_SIZE
    }

@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)"""
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_NAME,
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "beam"
            }
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""
    try:
        if llm is None:
            raise HTTPException(status_code=503, detail="Model not initialized")
        
        # Convert messages to prompt
        prompt = format_openai_prompt(request.messages)
        
        # Generate response
        outputs = llm.generate(
            prompts=[prompt],
            sampling_params=vllm.SamplingParams(
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                stop=["Human:", "System:"]
            )
        )
        
        if not outputs:
            raise HTTPException(status_code=500, detail="No output generated")
        
        output = outputs[0]
        generated_text = output.outputs[0].text.strip()
        
        # Create response in OpenAI format
        response = ChatCompletionResponse(
            id=f"chatcmpl-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            object="chat.completion",
            created=int(datetime.now().timestamp()),
            model=MODEL_NAME,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=generated_text),
                    finish_reason="stop"
                )
            ],
            usage={
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(generated_text.split()),
                "total_tokens": len(prompt.split()) + len(generated_text.split())
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Chat completion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/completions")
async def completions(request: CompletionRequest):
    """OpenAI-compatible completions endpoint"""
    try:
        if llm is None:
            raise HTTPException(status_code=503, detail="Model not initialized")
        
        # Generate response
        outputs = llm.generate(
            prompts=[request.prompt],
            sampling_params=vllm.SamplingParams(
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p
            )
        )
        
        if not outputs:
            raise HTTPException(status_code=500, detail="No output generated")
        
        output = outputs[0]
        generated_text = output.outputs[0].text.strip()
        
        # Create response in OpenAI format
        response = CompletionResponse(
            id=f"cmpl-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            object="text_completion",
            created=int(datetime.now().timestamp()),
            model=MODEL_NAME,
            choices=[
                CompletionChoice(
                    text=generated_text,
                    index=0,
                    finish_reason="stop"
                )
            ],
            usage={
                "prompt_tokens": len(request.prompt.split()),
                "completion_tokens": len(generated_text.split()),
                "total_tokens": len(request.prompt.split()) + len(generated_text.split())
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Completion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Beam endpoint configuration
@endpoint(
    gpu="A100-40" if GPU_COUNT == 1 else f"A100-40:{GPU_COUNT}",
    gpu_count=GPU_COUNT,
    keep_warm_seconds=300,
    env={
        "MODEL_NAME": MODEL_NAME,
        "MAX_MODEL_LEN": str(MAX_MODEL_LEN),
        "GPU_MEMORY_UTILIZATION": str(GPU_MEMORY_UTILIZATION),
        "TENSOR_PARALLEL_SIZE": str(TENSOR_PARALLEL_SIZE),
        "GPU_COUNT": str(GPU_COUNT)
    }
)
def main():
    """Main entry point for Beam deployment"""
    global llm
    
    # Initialize the model
    if not initialize_model():
        raise Exception("Failed to initialize vLLM model")
    
    # Start the FastAPI server
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", "8000")),
        log_level="info"
    )

if __name__ == "__main__":
    main()