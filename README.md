# comicxcomp
Software to compress and manage cbr and cbz files

File requirements:
The libraries that are not part of the standard installation of Python are: PILLOW and RARFILE

They are installed via pip:
pip install pillow
pip install rarfile

The unRAR.exe file is essential on Windows for proper management of cbr files (rar compression).
Replace the path of the rar file management tool in the following line on Linux or Mac:
    rarfile.UNRAR_TOOL = r'UnRAR.exe'

