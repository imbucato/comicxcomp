import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import rarfile
import zipfile
import tempfile
import shutil

#Definisco il percorso dell'eseguibile unrar.exe indispensabile per il funziomanento del modulo python 'rarfile'
rarfile.UNRAR_TOOL = r'UnRAR.exe'

#Funzione per riconoscere se un file è un archivio ZIP indipendemente dall'estensione
def is_zip_file(filename):
    try:
        with zipfile.ZipFile(filename) as zip_file:
            return True
    except zipfile.BadZipFile:
        return False

#Funzione per riconoscere se un file è un archivio RAR indipendemente dall'estensione
def is_rar_file(filename):
    try:
        with rarfile.RarFile(filename) as rar_file:
            return True
    except rarfile.NotRarFile:
        return False

#FUNZIONE PRINCIPALE PER LA COMPRESSIONE DEI CBR/CBZ
def compress_cb(input_file, output_file, max_size, dpi, jpg_quality, color_bits):
    print_status('Inizia compressione')

    archive = None
    archive_type = None

    #Verifica se il file in entrata è un archivio zip o rar valido e lo scompatta con il modulo python corretto
    if is_rar_file(input_file):
        archive = rarfile.RarFile
        archive_type = 'cbr'
        if input_file.lower().endswith('.cbr'):
            print_status('Archivio di tipo RAR')
        else:
            print_status('Il file ha estenzione cbz ma è in realtà un cbr (archivio RAR)')        
    elif is_zip_file(input_file):
        archive = zipfile.ZipFile
        archive_type = 'cbz'
        if input_file.lower().endswith('.zip'):
            print_status('Archivio di tipo ZIP')
        else:
            print_status('Il file ha estenzione cbr ma è in realtà un cbz (archivio ZIP)')
    else:
        print_status('Archivio non corretto o non supportato')
        return
    
    with archive(input_file, 'r') as af:
        temp_dir = tempfile.mkdtemp()
        print_status('Scompattazione archivio')
        af.extractall(temp_dir)
        pagina = 1
        new_temp_dir = tempfile.mkdtemp()
        for root, _, files in os.walk(temp_dir):
            print_status('Modifica immagini')
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(root, file)
                    
                    nome_immagine_senza_estensione = os.path.splitext(os.path.basename(image_path))[0]

                    output_image_path_jpg = os.path.join(new_temp_dir, nome_immagine_senza_estensione + '.jpg')
                    output_image_path_png = os.path.join(new_temp_dir, nome_immagine_senza_estensione + '.png')

                    img = Image.open(image_path)

                    if max(img.size) > max_size:
                        scale_factor = max_size / max(img.size)
                        new_size = tuple(int(x * scale_factor) for x in img.size)
                        img = img.resize(new_size, Image.LANCZOS)

                    if color_bits=='grigi' and 2 < pagina < len(files) - 1 and img.mode != '1':
                        img = img.convert("L");
                    elif color_bits=='bn' and 2 < pagina < len(files) - 1 and img.mode != '1':
                        img = img.convert("L");
                        img = img.convert("1");
                    
                    if img.mode == '1':
                        img.save(output_image_path_png, format="PNG", dpi=(dpi, dpi), compress_level=6) 
                    else:
                        img.save(output_image_path_jpg, 'JPEG', dpi=(dpi, dpi), quality=jpg_quality)          
                    
                    pagina += 1
        
        print_status('Ricreazione archivio compresso')
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as out_zip:
            for root, _, files in os.walk(new_temp_dir):
                for file in files:
                    out_zip.write(os.path.join(root, file), arcname=file)
    
        shutil.rmtree(temp_dir)
        shutil.rmtree(new_temp_dir)

        print_status('Fine compressione')

# Definisce una funzione per la selezione del file di input
def select_input_file():
    file_selected = filedialog.askdirectory()
    input_file_entry.delete(0, tk.END)
    input_file_entry.insert(0, file_selected)

# Definisce una funzione per la selezione del file di output
def select_output_file():
    file_selected = filedialog.askdirectory()
    output_file_entry.delete(0, tk.END)
    output_file_entry.insert(0, file_selected)

#Deginisce una funzione per stampare i messaggi di stato all'interno del box output_message
def print_status(message):
    output_message.configure(state='normal') 
    output_message.insert(tk.END, message + "\n")
    output_message.see(tk.END)
    output_message.update()    
    output_message.configure(state='disabled') 

# Definisce la funzione che avvia la compressione
def avvia_compressione():
     
    input_dir = input_file_entry.get()
    output_dir = output_file_entry.get()
    max_size = int(long_side_entry.get())
    dpi = int(dpi_entry.get())
    jpg_quality = int(jpg_comp_entry.get())
    color_bits = radio_var.get()

    print_status('*******INIZIO PROCESSO COMPRESSIONE BATCH*******')

    for file in os.listdir(input_dir):
        if file.endswith('.cbr') or file.endswith('.cbz'):
            
            input_file = os.path.join(input_dir, file)
            nome_file_senza_estensione = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(output_dir, nome_file_senza_estensione + '.cbz')
            print_status('ELABORAZIONE ' + input_file)
            compress_cb(input_file, output_file, max_size, dpi, jpg_quality, color_bits)

    print_status('*******FINE PROCESSO COMPRESSIONE BATCH*******')  

 
    

#root.title("undefined")
width=592
height=624

#setting window size
window = tk.Tk()
window.title("Comrpimi cbr/cbz singolo")
window.geometry('%dx%d' % (width, height))
window.resizable(width=False, height=False)
screenwidth = window.winfo_screenwidth()
screenheight = window.winfo_screenheight()

alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
window.geometry(alignstr)

# Crea i widget per la selezione della directory di input
input_file_label = tk.Label(window, text="Seleziona la directory che contiene i cbr/cbz")
input_file_label.place(x=10,y=0,height=30)
input_file_entry = tk.Entry(window)
input_file_entry.place(x=10,y=30,width=486,height=30)
input_file_button = tk.Button(window, text="Sfoglia", command=select_input_file)
input_file_button.place(x=510,y=30,width=70,height=30)

# Crea i widget per la selezione della directory di output
output_file_label = tk.Label(window, text="Seleziona la directory dove salvare i cbz compressi")
output_file_label.place(x=10,y=70,height=30)
output_file_entry = tk.Entry(window)
output_file_entry.place(x=10,y=100,width=487,height=30)
output_file_button = tk.Button(window, text="Sfoglia", command=select_output_file)
output_file_button.place(x=510,y=100,width=70,height=30)

# Crea i widget per l'inserimento dei parametri di compressione
long_side_label = tk.Label(window, text="Dimensione lato lungo")
long_side_label.place(x=0,y=140,width=151,height=30)
long_side_entry = tk.Entry(window)
long_side_entry.place(x=30,y=170,width=92,height=30)

dpi_label = tk.Label(window, text="DPI")
dpi_label.place(x=170,y=140,width=70,height=30)
dpi_entry = tk.Entry(window)
dpi_entry.place(x=170,y=170,width=70,height=30)

jpg_comp_label = tk.Label(window, text="Compressione JPEG")
jpg_comp_label.place(x=250,y=140,width=140,height=30)
jpg_comp_entry = tk.Entry(window)
jpg_comp_entry.place(x=280,y=170,width=70,height=30)

# Crea i widget per la selezione delle radiobox colore/scala di grigi/bw
GLabel_183=tk.Label(window)
GLabel_183["justify"] = "center"
GLabel_183["text"] = "Colore"
GLabel_183.place(x=390,y=140,width=70,height=30)

GLabel_58=tk.Label(window)
GLabel_58["justify"] = "center"
GLabel_58["text"] = "Scala grigi"
GLabel_58.place(x=460,y=140,width=70,height=30)

GLabel_417=tk.Label(window)
GLabel_417["justify"] = "center"
GLabel_417["text"] = "B/W"
GLabel_417.place(x=530,y=140,width=70,height=30)

radio_var = tk.StringVar()
radio_colori = tk.Radiobutton(window, variable=radio_var, value='colori')
radio_colori.place(x=380,y=170,width=85,height=25)

radio_grigi = tk.Radiobutton(window, variable=radio_var, value='grigi')
radio_grigi.place(x=450,y=170,width=85,height=25)

radio_bn = tk.Radiobutton(window, variable=radio_var, value='bn')
radio_bn.place(x=520,y=170,width=85,height=25)

radio_var.set('colori')     #imposto colori come valore di default

# Crea il widget per il pulsante di conferma
#confirm_button = tk.Button(window, text="AVVIA", command=window.quit)
confirm_button = tk.Button(window, text="AVVIA", command=avvia_compressione)
confirm_button.place(x=250,y=220,width=110,height=30)

# Crea il widget text per la stampa dei messaggi di stato
output_message = tk.Text(window)

scrollbar = tk.Scrollbar(window)
scrollbar.config(command=output_message.yview)

output_message.config(yscrollcommand=scrollbar.set)

output_message.place(x=30,y=270,width=530,height=331)
scrollbar.place(x=550,y=270,width=20,height=331)
output_message.configure(state='disabled')



# Avvia il loop principale della GUI
window.mainloop()