# SETUP
## Install Python Packages
### Run:
```bash
pip install -r requirements.txt
```

## Install CUDA-enabled torch version
* NOTE: currently requires an NVIDIA GPU.
* OPTIONAL: Manually installing the [CUDA toolkit](https://developer.nvidia.com/cuda-downloads) may be required depending on your installed NVIDIA driver version.
### Run:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```
(or visit [Pytorch getting started](https://pytorch.org/get-started/locally/) for different versions of CUDA)
