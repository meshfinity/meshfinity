#!/bin/bash

mkdir -p autoremesher/mac
wget -O autoremesher/mac/autoremesher-8fdfb7e-mac.zip "https://github.com/meshfinity/autoremesher/releases/download/8fdfb7e/autoremesher-8fdfb7e-mac.zip"
unzip autoremesher/mac/autoremesher-8fdfb7e-mac.zip -d autoremesher/mac

cd gui
npm i -D
npm run build
cd ..

arch --x86_64 /usr/local/bin/brew install python@3.12
arch --x86_64 /usr/local/bin/python3.12 -m venv venv
source venv/bin/activate

arch --x86_64 pip install torch torchvision
arch --x86_64 pip install omegaconf pillow einops transformers trimesh rembg vtk moderngl pywebview requests huggingface-hub
arch --x86_64 pip uninstall -y rembg # We need rembg's dependencies, but we want to use our custom rembg_offline instead of the original rembg, so uninstall the original
arch --x86_64 pip uninstall -y numpy
arch --x86_64 pip install numpy==1.26.4
arch --x86_64 pip install pyinstaller

arch --x86_64 pyinstaller main.py --noupx --hidden-import tsr --hidden-import tsr.system --hidden-import tsr.utils --hidden-import tsr.models --hidden-import tsr.models.isosurface --hidden-import tsr.models.nerf_renderer --hidden-import tsr.models.network_utils --hidden-import tsr.models.tokenizers --hidden-import tsr.models.tokenizers.image --hidden-import tsr.models.tokenizers.triplane --hidden-import tsr.models.transformer --hidden-import tsr.models.transformer.attention --hidden-import tsr.models.transformer.basic_transformer_block --hidden-import tsr.models.transformer.transformer_1d --add-data "gui/build:gui_build" --add-data "autoremesher:autoremesher"
cp -r venv/lib/python3.12/site-packages/vtkmodules/util dist/main/_internal/vtkmodules

mv dist/main dist/meshfinity-release
# After this runs, in the GitHub Actions script, We will rename `dist/meshfinity-release` to contain the version number
# Then we will use `ditto` to compress this to a ZIP archive.
