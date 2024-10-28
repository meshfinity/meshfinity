#!/bin/bash

mkdir -p autoremesher/mac
wget -O autoremesher/mac/autoremesher-8fdfb7e-mac.zip "https://github.com/meshfinity/autoremesher/releases/download/8fdfb7e/autoremesher-8fdfb7e-mac.zip"
unzip autoremesher/mac/autoremesher-8fdfb7e-mac.zip -d autoremesher/mac

mkdir -p checkpoints/u2net
wget -O checkpoints/u2net/u2net.onnx "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx"
mkdir -p checkpoints/tsr
wget -O checkpoints/tsr/config.yaml "https://huggingface.co/stabilityai/TripoSR/resolve/main/config.yaml?download=true"
wget -O checkpoints/tsr/model.ckpt "https://huggingface.co/stabilityai/TripoSR/resolve/main/model.ckpt?download=true"
mkdir -p checkpoints/dino-vitb16
wget -O checkpoints/dino-vitb16/preprocessor_config.json "https://huggingface.co/facebook/dino-vitb16/resolve/main/preprocessor_config.json?download=true"
wget -O checkpoints/dino-vitb16/config.json "https://huggingface.co/facebook/dino-vitb16/resolve/main/config.json?download=true"
wget -O checkpoints/dino-vitb16/pytorch_model.bin "https://huggingface.co/facebook/dino-vitb16/resolve/main/pytorch_model.bin?download=true"

brew install python@3.10
pip3.10 install virtualenv
python3.10 -m virtualenv venv
source venv/bin/activate

pip install torch torchvision
pip install omegaconf pillow einops transformers trimesh rembg vtk moderngl pywebview requests cx_Freeze
pip uninstall -y rembg # We need rembg's dependencies, but we want to use our custom rembg_offline instead of the original rembg, so uninstall the original

cxfreeze main.py --target-dir=dist --target-name=Meshfinity --packages=torch
