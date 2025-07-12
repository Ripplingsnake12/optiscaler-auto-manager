#!/bin/bash

echo "Creating FSR4 DLL directory structure..."

# Create the bundled FSR4 DLLs directory
mkdir -p "fsr4_dlls/FSR 4.0"
mkdir -p "fsr4_dlls/FSR 4.0.1"

echo "Directory structure created:"
echo "fsr4_dlls/"
echo "├── FSR 4.0/"
echo "│   └── amdxcffx64.dll (place FSR 4.0 DLL here)"
echo "└── FSR 4.0.1/"
echo "    └── amdxcffx64.dll (place FSR 4.0.1 DLL here)"
echo
echo "To use:"
echo "1. Place your FSR 4.0 amdxcffx64.dll in fsr4_dlls/FSR 4.0/"
echo "2. Place your FSR 4.0.1 amdxcffx64.dll in fsr4_dlls/FSR 4.0.1/"
echo "3. Run the OptiScaler manager to select versions"