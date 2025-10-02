if NOT EXIST ".venv\Scripts\activate.bat" (
    RD ".venv"
)
if NOT EXIST ".venv" (
    python -m venv ".venv"
)
call ".venv\Scripts\activate.bat"
pip install -r requirements.txt
pip install pyinstaller
python build.py
