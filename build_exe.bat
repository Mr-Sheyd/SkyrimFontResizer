@echo off
rem Пересборка SkyrimFontResizer.exe из исходника (нужен Python 3.10+ с галочкой Add to PATH)
python -m pip install pyinstaller tkinterdnd2
python -m PyInstaller --noconfirm --onefile --windowed --name SkyrimFontResizer --collect-all tkinterdnd2 SkyrimFontResizer.py
echo.
echo Готово: dist\SkyrimFontResizer.exe
pause