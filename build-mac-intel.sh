#!/bin/bash

mkdir -p autoremesher/mac
wget -O autoremesher/mac/autoremesher-7e26f98-mac.zip "https://github.com/meshfinity/autoremesher/releases/download/7e26f98/autoremesher-7e26f98-mac.zip"
unzip autoremesher/mac/autoremesher-7e26f98-mac.zip -d autoremesher/mac
rm -rf autoremesher/mac/autoremesher-7e26f98-mac
rm autoremesher/mac/autoremesher-7e26f98-mac.zip

cd gui
npm i -D
npm run build
cd ..

arch --x86_64 /usr/local/bin/python3.12 -m venv venv
source venv/bin/activate

arch --x86_64 pip install torch torchvision
arch --x86_64 pip install omegaconf pillow einops transformers trimesh "rembg[cpu]" vtk moderngl pywebview requests huggingface-hub filelock wakepy miniaudio
arch --x86_64 pip uninstall -y rembg # We need rembg's dependencies, but we want to use our custom rembg_offline instead of the original rembg, so uninstall the original
arch --x86_64 pip uninstall -y numpy
arch --x86_64 pip install numpy==1.26.4
arch --x86_64 pip install pyinstaller

arch --x86_64 pyinstaller main.py --optimize 2 --noupx --windowed --icon branding/icon.png -n Meshfinity --hidden-import vtkmodules --hidden-import vtkmodules.vtkFiltersCore --hidden-import vtkmodules.vtkIOGeometry --hidden-import vtkmodules.vtkCommonCore --hidden-import vtkmodules.vtkCommonDataModel --hidden-import vtkmodules.vtkCommonExecutionModel --hidden-import vtkmodules.vtkCommonTransforms --hidden-import vtkmodules.vtkCommonMath --hidden-import vtkmodules.vtkCommonMisc --hidden-import vtkmodules.vtkIOCore --hidden-import vtkmodules.vtkIOLegacy --hidden-import vtkmodules.util --hidden-import vtkmodules.util.numpy_support --hidden-import tsr --hidden-import tsr.system --hidden-import tsr.utils --hidden-import tsr.models --hidden-import tsr.models.isosurface --hidden-import tsr.models.nerf_renderer --hidden-import tsr.models.network_utils --hidden-import tsr.models.tokenizers --hidden-import tsr.models.tokenizers.image --hidden-import tsr.models.tokenizers.triplane --hidden-import tsr.models.transformer --hidden-import tsr.models.transformer.attention --hidden-import tsr.models.transformer.basic_transformer_block --hidden-import tsr.models.transformer.transformer_1d --add-data "gui/build:gui_build" --add-data "autoremesher:autoremesher" --add-data "sounds:sounds"
cp -r venv/lib/python3.12/site-packages/vtkmodules/util dist/Meshfinity.app/Contents/Frameworks/vtkmodules

# After this runs, in the GitHub Actions script, we will create a folder with the version number in the name.
# Then we will copy `dist/Meshfinity.app` into this folder, and use `ditto` to compress it to a ZIP archive, which will be released.
