## MIDI Visualizer

**MIDI Visualizer** is a real-time video processing application designed to create visually compelling videos of piano performances. It features GPU-accelerated video decoding and encoding, fully synchronized with audio and MIDI input. Thanks to ModernGL, OpenCV CUDA, and NVIDIA's Video Processing Framework (PyNvCodec), the application delivers high-performance visuals with stunning effects. 

Users can easily adjust video settings, colors, and visual styles to suit their preferences. Additional customization options are planned for future updates.

---

## Features

- ⚡ GPU-accelerated video decoding and encoding  
- 🎹 Real-time piano and note visualizations with dynamic lighting and particle effects  
- 🎬 OpenGL-based rendering using ModernGL  
- 🎧 Audio and video synchronization with millisecond-level precision  
- 📽️ Real-time recording support  

---

## Project Structure

- `assets/` – Video, audio, and MIDI files  
- `settings/` – Color and video configuration files  
- `VPF OpenCV Interop/` – Custom-modified VPF backend for OpenCV and ModernGL
- `ModernGL shaders/` – Vertex and fragment shader files  
- `src/` – Main application (Python code)  

---

## Requirements

- Python 3.12  
- NVIDIA GPU with CUDA support (v12.8+)  
- OpenCV built with CUDA  
- NVIDIA Video Processing Framework (PyNvCodec)  
- ModernGL and ModernGL Window  
- PyCUDA (with OpenGL interop enabled), NumPy, Pygame, etc.  
- FFmpeg

## Getting Started

- Move the .hpp and .cpp files under VPF OpenCV folders into VideoProcessingFramework's respective folders

## Current state of the project

- Needs further optimization and customization
- The project will be updated in the future
