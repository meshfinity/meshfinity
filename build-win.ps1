mkdir autoremesher/win
Invoke-WebRequest "https://github.com/meshfinity/autoremesher/releases/download/7e26f98/autoremesher-7e26f98-win.zip" -OutFile autoremesher/win/autoremesher-7e26f98-win.zip
Expand-Archive autoremesher/win/autoremesher-7e26f98-win.zip -DestinationPath autoremesher/win
del autoremesher/win/autoremesher-7e26f98-win.zip
robocopy /E /MOV autoremesher/win/autoremesher-7e26f98-win autoremesher/win
rmdir autoremesher/win/autoremesher-7e26f98-win

cd gui
npm i -D
npm run build
cd ..

python -m venv venv
venv\Scripts\activate.ps1

pip install torch torchvision
pip install omegaconf pillow einops transformers trimesh "rembg[cpu]" vtk moderngl pywebview requests huggingface-hub filelock wakepy miniaudio
pip uninstall -y rembg
pip uninstall -y numpy
pip install numpy==1.26.4
pip install pyinstaller

pyinstaller main.py --optimize 2 --noupx --windowed --icon branding/icon.png --splash branding/splash.png -n Meshfinity --hidden-import vtkmodules --hidden-import vtkmodules.vtkFiltersCore --hidden-import vtkmodules.vtkIOGeometry --hidden-import vtkmodules.vtkCommonCore --hidden-import vtkmodules.vtkCommonDataModel --hidden-import vtkmodules.vtkCommonExecutionModel --hidden-import vtkmodules.vtkCommonTransforms --hidden-import vtkmodules.vtkCommonMath --hidden-import vtkmodules.vtkCommonMisc --hidden-import vtkmodules.vtkIOCore --hidden-import vtkmodules.vtkIOLegacy --hidden-import vtkmodules.util --hidden-import vtkmodules.util.numpy_support --hidden-import tsr --hidden-import tsr.system --hidden-import tsr.utils --hidden-import tsr.models --hidden-import tsr.models.isosurface --hidden-import tsr.models.nerf_renderer --hidden-import tsr.models.network_utils --hidden-import tsr.models.tokenizers --hidden-import tsr.models.tokenizers.image --hidden-import tsr.models.tokenizers.triplane --hidden-import tsr.models.transformer --hidden-import tsr.models.transformer.attention --hidden-import tsr.models.transformer.basic_transformer_block --hidden-import tsr.models.transformer.transformer_1d --add-data "gui/build:gui_build" --add-data "autoremesher:autoremesher" --add-data "sounds:sounds"
robocopy /E venv/Lib/site-packages/vtkmodules/util dist/Meshfinity/_internal/vtkmodules/util
