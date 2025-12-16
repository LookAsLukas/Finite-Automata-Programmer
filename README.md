# FAP - The Finite Automata Programmer
## About the product
Finite Automata Programmer (FAP) - is an IDE for DFAs, NFAs and e-NFAs. It provides a user friendly
graphical interface for building, running and debugging automata. It also has a regex-FA converter
(and vise-versa) and a DFA minimalizer  
## Installation and build
For a quick ready-to-go usage just download the executable file from Releases

For building it yourself:
1. Clone the repo
2. Run `run_build_linux.sh` if on Linux or `run_build_windows.bat` if on Windows
  
Note that these scrips will first setup the venv and then compile an executable  
Another option would be to create the venv yourself, download requirements from `requirements.txt`
and just run 
``` bash
python src/fap.py
```
