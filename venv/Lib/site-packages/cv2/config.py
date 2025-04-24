import os

BINARIES_PATHS = [
    os.path.join('C:/Users/ihsan/Projects/Synthesia/opencv/build/install', 'x64/vc17/bin'),
    os.path.join(os.getenv('CUDA_PATH', 'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.8'), 'bin')
] + BINARIES_PATHS
