pyinstaller --distpath ./build --onefile --icon=ico-batch.ico --add-data "ico-batch.ico;." --noconsole .\comixcomp-b.py

pyinstaller --distpath ./build --onefile --icon=ico.ico --add-data "ico.ico;." --noconsole .\comixcomp.py

pyinstaller --distpath ./build --onefile --icon=ico-batch.ico --add-data "UnRAR.exe" --noconsole .\comixcomp-b.py

pyinstaller --distpath ./build --onefile --icon=ico-batch.ico --add-data "UnRAR.exe" --noconsole .\comixcomp.py