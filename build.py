#!/usr/bin/env python3
import os
import platform
import subprocess
import sys
from pathlib import Path

def build_app():
    """Build the automata builder application with PyInstaller"""
    
    # Get the current directory
    current_dir = Path(__file__).parent
    main_script = current_dir / "fap.py"
    
    if not main_script.exists():
        print(f"Error: Main script {main_script} not found!")
        return False
    
    # Platform-specific configuration
    system = platform.system().lower()
    app_name = "AutomataBuilder"
    
    # Common PyInstaller arguments
    common_args = [
        '--name', app_name,
        '--onefile',
        '--windowed',  # No console window
        '--clean',
        '--noconfirm',
    ]
    
    # Platform-specific arguments
    if system == 'windows':
        icon_file = current_dir / 'icon.ico'
        if icon_file.exists():
            common_args.extend(['--icon', str(icon_file)])
        common_args.extend(['--add-data', f'{current_dir / "icon.ico"};.'])
        
    elif system == 'darwin':  # macOS
        icon_file = current_dir / 'icon.icns'
        if icon_file.exists():
            common_args.extend(['--icon', str(icon_file)])
        common_args.extend([
            '--add-data', f'{current_dir / "icon.icns"}:.',
            '--osx-bundle-identifier', 'com.automata.builder'
        ])
        
    elif system == 'linux':
        icon_file = current_dir / 'icon.png'
        if icon_file.exists():
            common_args.extend(['--icon', str(icon_file)])
    
    # Add hidden imports for Flet and automata-lib
    hidden_imports = [
        'flet',
        'flet.core',
        'automata',
        'automata.fa.dfa',
        'automata.fa.nfa',
        'graphviz',
        'pygraphviz',
        'typing_extensions',
    ]
    
    for imp in hidden_imports:
        common_args.extend(['--hidden-import', imp])
    
    # Final command
    pyinstaller_args = ['pyinstaller'] + common_args + [str(main_script)]
    
    print("Building application with PyInstaller...")
    print(f"Command: {' '.join(pyinstaller_args)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(pyinstaller_args, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        
        # Show output location
        dist_dir = current_dir / 'dist'
        if system == 'windows':
            exe_path = dist_dir / f"{app_name}.exe"
        else:
            exe_path = dist_dir / app_name
            
        print(f"\nApplication created at: {exe_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: PyInstaller not found. Please install it with: pip install pyinstaller")
        return False

if __name__ == "__main__":
    build_app()
