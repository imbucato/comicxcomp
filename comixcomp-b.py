import os
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import rarfile
import zipfile
import tempfile
import shutil
import multiprocessing
from multiprocessing import Pool

#Definisco il percorso dell'eseguibile unrar.exe indispensabile per il funziomanento del modulo python 'rarfile'
if sys.platform.startswith('win'):
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

def elabora_immagine(max_size, dpi, jpg_quality, color_bits,new_temp_dir, pagine, pagina, file):
    
    nome_immagine_senza_estensione = os.path.splitext(os.path.basename(file))[0]
    pagina = pagina + 1
    
    output_image_path_jpg = os.path.join(new_temp_dir, nome_immagine_senza_estensione + '.jpg')
    output_image_path_png = os.path.join(new_temp_dir, nome_immagine_senza_estensione + '.png')

    img = Image.open(file)

    #Se la dimensione del lato lungo inserita dall'utente è minore della dimensione originale l'immagine viene scalata                
    if max(img.size) > max_size:
        scale_factor = max_size / max(img.size)
        new_size = tuple(int(x * scale_factor) for x in img.size)
        img = img.resize(new_size, Image.LANCZOS)

    #if img.info['dpi'] < dpi: dpi=img.info['dpi']

    #Determinazione del compression level per il salvataggio in PNG
    comp_level_png = int((100-jpg_quality)/10)
    if comp_level_png == 10: comp_level_png=9

    #Se è stata selezionata la modalità "bianco e nero" vengono lasciate a colori solo prima, seconda, terza e quarta di copertina
    #Le altre immagini vengono convertite in scala di grigi ad 8 tonalità
    if color_bits=='B/N' and 2 < pagina < pagine - 1 and img.mode != '1':
        if img.mode != 'P' or img.getcolors(maxcolors=256) is None:
            img = img.convert('L')
            img = img.quantize(8)

    #Se l'immagine è in b/n, scala di grigi o modalità Palette viene salvata in PNG               
    if img.mode == '1' or img.mode == 'P' or img.mode == 'L':
        img.save(output_image_path_png, format="PNG", dpi=(dpi, dpi), compress_level=comp_level_png) 
    #Altrimenti viene convertita in RBA (nel caso in cui sia in RGBA) e salvata in JPEG
    else:
        if img.mode == "RGBA" : 
            img=img.convert("RGB")
        img.save(output_image_path_jpg, 'JPEG', dpi=(dpi, dpi), quality=jpg_quality)    


#FUNZIONE PRINCIPALE PER LA COMPRESSIONE DEI CBR/CBZ
def compress_cb(input_file, output_file, max_size, dpi, jpg_quality, color_bits):
    
    if cancella_compressione:
        print_status("Compressione annullata")
        return

    archive = None
    archive_type = None

    #Verifica se il file in entrata è un archivio zip o rar valido e lo scompatta con il modulo python corretto
    if is_rar_file(input_file):
        archive = rarfile.RarFile
        archive_type = 'cbr'
        if input_file.lower().endswith('.cbr'):
            print_status('....Archivio di tipo RAR')
        else:
            print_status('Il file ha estenzione cbz ma è in realtà un cbr (archivio RAR)')        
    elif is_zip_file(input_file):
        archive = zipfile.ZipFile
        archive_type = 'cbz'
        if input_file.lower().endswith('.zip'):
            print_status('....Archivio di tipo ZIP')
        else:
            print_status('....Il file ha estenzione cbr ma è in realtà un cbz (archivio ZIP)')
    else:
        print_status('....Archivio non corretto o non supportato')
        return
    
    with archive(input_file, 'r') as af:
        temp_dir = tempfile.mkdtemp()
        print_status('....Scompattazione archivio')
        af.extractall(temp_dir)
        pagina = 1
        new_temp_dir = tempfile.mkdtemp()
        
        lista_file = []
        
        for root, _, files in os.walk(temp_dir):
            print_status('....Modifica immagini')
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(root, file)
                    lista_file.append(image_path)
        
        #Avvio del multiprocessing per la conversione delle immagini           
        with Pool() as pool:
            pool.starmap(elabora_immagine, [(max_size, dpi, jpg_quality, color_bits, new_temp_dir, len(lista_file)+1, i, file,) for i, file in enumerate(lista_file)])
        
        print_status('....Ricreazione archivio compresso')
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as out_zip:
            for root, _, files in os.walk(new_temp_dir):
                for file in files:
                    out_zip.write(os.path.join(root, file), arcname=file)
    
        shutil.rmtree(temp_dir)
        shutil.rmtree(new_temp_dir)

        print_status('....Fine compressione')

# Definisce una funzione per la selezione del file di input
def select_input_file():
    file_selected = filedialog.askdirectory()
    input_file_entry.configure(state='normal')
    input_file_entry.delete(0, tk.END)
    input_file_entry.insert(0, file_selected)
    input_file_entry.configure(state='disabled')

# Definisce una funzione per la selezione del file di output
def select_output_file():
    file_selected = filedialog.askdirectory()
    output_file_entry.configure(state='normal')
    output_file_entry.delete(0, tk.END)
    output_file_entry.insert(0, file_selected)
    output_file_entry.configure(state='disabled')

#Deginisce una funzione per stampare i messaggi di stato all'interno del box output_message
def print_status(message):
    output_message.configure(state='normal') 
    output_message.insert(tk.END, message + "\n")
    output_message.see(tk.END)
    output_message.update()    
    output_message.configure(state='disabled') 

# Definisce la funzione che interrompe il processo batch
def annulla_compressione():
    global cancella_compressione
    cancella_compressione = True 

# Definisce la funzione che avvia la compressione
def avvia_compressione():
    global cancella_compressione
    
    cancella_compressione = False
    avvia = True

    input_dir = input_file_entry.get()
    output_dir = output_file_entry.get()
    max_size = long_side_entry.get()
    dpi = int(dpi_entry.get())
    jpg_quality = compressione_jpg.get()
    color_bits = radio_var.get()

    #Verifica se il file di input esiste
    if not os.path.isdir(input_dir):
        print_status("La directory di INPUT non sembra esistere!")
        avvia = False

    #Verifica se la directory di output esiste
    if not os.path.isdir(output_dir):
        print_status("La directory di OUTPUT non sembra esistere!")
        avvia = False

    if input_dir == output_dir:
        print_status("Le directory di INPUT e di OUTPUT non possono coincidere!")
        avvia = False

    #Verifica che il lato lungo dell'immagine sia stato inserito correttamente
    if max_size and 400 <= int(max_size) <= 4000:
        max_size=int(max_size)
    else:
        if not max_size:
            print_status("Inserire la dimensione del lato lungo per le immagini")
        else:
            print_status("Il lato lungo dell'immagine deve essere compreso tra 400 e 4000 px")
        avvia = False

    if avvia:
        inizio = time.time()
        print_status('*******INIZIO PROCESSO COMPRESSIONE BATCH*******')

        for file in os.listdir(input_dir):
            if file.endswith('.cbr') or file.endswith('.cbz'):
                
                input_file = os.path.join(input_dir, file)
                nome_file_senza_estensione = os.path.splitext(os.path.basename(input_file))[0]
                output_file = os.path.join(output_dir, nome_file_senza_estensione + '.cbz')
                print_status('\nELABORAZIONE ' + input_file)
                
                compress_cb(input_file, output_file, max_size, dpi, jpg_quality, color_bits)
                
                #    print_status('Si è verficato un errore imprevisto durante la compressione')

        fine = time.time()
        durata = int(fine-inizio)
        print_status('\n*******FINE PROCESSO COMPRESSIONE BATCH*******')  
        print_status(f'Elaborazione durata {durata} secondi')  


#COSTRUZIONE FINESTRA ISTRUZIONI
def apri_finestra_istruzioni():
    width_help=590
    height_help=440

    #Definisco la finestra w_help come variabile globale
    global w_help

    w_help = tk.Toplevel(window)
    w_help.title("Istruzioni")
    w_help.geometry('%dx%d' % (width_help, height_help))
    w_help.resizable(width=False, height=False)

    output_message = tk.Text(w_help,wrap="word")
    output_message.place(x=30,y=10,width=530,height=420)
    output_message.insert(tk.END, "Questo tool serve a comprimere in serie file cbr/cbz. Il software salva i file originali nel formato cbz (compressione zip) indipendentemente dal formato del file di origine.\n")
    output_message.insert(tk.END, "\nISTRUZIONI\n")
    output_message.insert(tk.END, "\n1) Selezionare la cartella di origine dei file cbr/cbz.\n")
    output_message.insert(tk.END, "\n2) Selezionare la cartella dove salvare i file compressi.\n")
    output_message.insert(tk.END, "\n3) Indicare il lato lungo delle immagini. Scegliere un valore compreso tra 600 e 4000 px. Se il fumetto originale ha pagine il cui lato lungo è maggiore di tale valore queste verranno ridimensionate.\n")
    output_message.insert(tk.END, "\n4) Selezionare il tipo di fumetto in entrata. Se il fumetto è in bianco e nero verranno \nmantenute a colori solo le prime due pagine e le ultime due. Le altre pagine verranno convertite in 8 tonalità di grigio e verrà utilizzato il formato PNG per il salvataggio delle immagini.\n")
    output_message.insert(tk.END, "\n5) Seleziona la qualità delle immagini. 100 corrisponde alla qualità massima. Corrisponde alla minima compressione per i JPEG e al livello di compressione 0 per il formato PNG. Per fumetti a colori si consiglia di usare valori non superiori a 85 mentre per fumetti b/n si ottengono ottimi risultati già con valori pari a 40-50.\n")
    output_message.insert(tk.END, "\n6) Selezionare i DPI dell'immagine. Buoni risultati si hanno già per valori pari a 150.\n")
    output_message.see(tk.END)
    output_message.update() 

# Definisci la funzione che verrà eseguita quando si seleziona "File -> Esci"
def exit_app():
    window.destroy()

def chiudi_finestra_istruzioni():
    if 'w_help' in globals():
        w_help.destroy()

def messaggio_info():
    email = "roby1976@gmail.com"
    website = "https://github.com/imbucato/comixcomp"

    messagebox.showinfo("Informazioni", f"Info: {email}\nRepository: {website}")

if __name__ == '__main__':
    # chiamare freeze_support() solo sotto Windows e solo
    # quando si utilizza un ambiente congelato
    if sys.platform.startswith('win') and getattr(sys, 'frozen', False):
        multiprocessing.freeze_support()
        
    width=592
    height=640

    #setting window size
    window = tk.Tk()
    if os.path.isfile('ico-batch.ico'): window.iconbitmap('ico-batch.ico')
    window.title("Comrpimi file cbr/cbz in serie")
    window.geometry('%dx%d' % (width, height))
    window.resizable(width=False, height=False)
    screenwidth = window.winfo_screenwidth()
    screenheight = window.winfo_screenheight()

    alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    window.geometry(alignstr)

    # Crea la barra dei menu
    menu_bar = tk.Menu(window)

    # Aggiungi il menu "File"
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Apri directory", command=select_input_file)
    file_menu.add_command(label="Directory output", command=select_output_file)
    file_menu.add_command(label="Esci", command=exit_app)
    menu_bar.add_cascade(label="File", menu=file_menu)

    # Aggiungi il menu "Info"
    options_menu = tk.Menu(menu_bar, tearoff=0)
    options_menu.add_command(label="Guida", command=apri_finestra_istruzioni)
    options_menu.add_command(label="Info", command=messaggio_info)
    menu_bar.add_cascade(label="Info", menu=options_menu)

    # Associa la barra dei menu alla finestra
    window.config(menu=menu_bar)

    # Crea i widget per la selezione del file di input
    input_file_label = tk.Label(window, text="Seleziona la directory contenente i cbr/cbz da comprimere")
    input_file_label.place(x=10,y=0,height=30)
    input_file_entry = tk.Entry(window)
    input_file_entry.configure(state='disabled')
    input_file_entry.place(x=10,y=30,width=486,height=30)
    input_file_button = tk.Button(window, text="Sfoglia", command=select_input_file)
    input_file_button.place(x=510,y=30,width=70,height=30)

    # Crea i widget per la selezione del file di output
    output_file_label = tk.Label(window, text="Scegli la directory dove salvare i cbz compressi")
    output_file_label.place(x=10,y=70,height=30)
    output_file_entry = tk.Entry(window)
    output_file_entry.configure(state='disabled')
    output_file_entry.place(x=10,y=100,width=487,height=30)
    output_file_button = tk.Button(window, text="Sfoglia", command=select_output_file)
    output_file_button.place(x=510,y=100,width=70,height=30)

    #Funzione di validazione del campo "long_side_entry": impedisce che vengano inserite lettere
    def validate_input(new_value):
        if new_value.isnumeric() or new_value == "":
            return True
        else:
            return False

    vcmd = (window.register(validate_input), '%P')

    # Crea i widget per l'inserimento dei parametri di compressione
    long_side_label = tk.Label(window, text="Dimensione lato lungo")
    long_side_label.place(x=0,y=140,width=151,height=30)
    long_side_entry = tk.Entry(window,validate="key", validatecommand=vcmd)
    long_side_entry["justify"] = "center"
    long_side_entry.place(x=30,y=170,width=92,height=30)

    dpi_label = tk.Label(window, text="DPI")
    dpi_label.place(x=170,y=140,width=70,height=30)

    #Variabile per memorizzare il valore selezionato dall'elenco a discesa
    selected_value = tk.StringVar()
    options = [72, 96, 120, 150, 200, 220, 300, 400, 600]
    selected_value.set(options[0])
    dpi_entry = ttk.Combobox(window,textvariable=selected_value, values=options)
    dpi_entry["justify"] = "center"
    dpi_entry.place(x=170,y=170,width=70,height=30)

    jpg_comp_label = tk.Label(window, text="Qualità")
    jpg_comp_label.place(x=250,y=140,width=140,height=30)

    compressione_jpg = tk.IntVar(value=85)
    jpg_comp_entry = tk.Scale(window, from_=1, to=100, orient=tk.HORIZONTAL, variable=compressione_jpg)
    jpg_comp_entry.place(x=260,y=160,width=120)

    # Crea i widget per la selezione della tipologia di fumetto in entrata
    GLabel_58=tk.Label(window)
    GLabel_58["justify"] = "center"
    GLabel_58["text"] = "Tipologia fumetto in entrata"
    GLabel_58.place(x=400,y=140,width=160,height=30)

    radio_var = tk.StringVar()
    radio_colori = tk.Radiobutton(window, variable=radio_var, value='colori', text='Colori')
    radio_colori.place(x=390,y=170,width=100,height=25)

    radio_grigi = tk.Radiobutton(window, variable=radio_var, value='B/N', text='B/N')
    radio_grigi.place(x=480,y=170,width=85,height=25)

    radio_var.set('colori')     #imposto colori come valore di default

    # Crea il widget per il pulsante di conferma
    confirm_button = tk.Button(window, text="AVVIA", command=avvia_compressione)
    confirm_button.place(x=250,y=220,width=110,height=30)

    #Crea il widget per il pulsante di annulla
    cancel_button = tk.Button(window, text="Annulla", command=annulla_compressione)
    cancel_button.place(x=370,y=220,width=110,height=30)

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