import torch

# Check if CUDA is available
cuda_available = torch.cuda.is_available()
print(f"CUDA Available: {cuda_available}")

# Check the number of GPUs
gpu_count = torch.cuda.device_count()
print(f"GPU Count: {gpu_count}")

# Get the name of the GPU
if cuda_available:
    for i in range(gpu_count):
        print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
