import tkinter as tk
from tkinter import filedialog

# Definisce una funzione per la selezione del file di input
def select_input_file():
    file_selected = filedialog.askopenfilename(filetypes=[("cbz file", ".cbz"),("cbr file", ".cbr")])
    input_file_entry.delete(0, tk.END)
    input_file_entry.insert(0, file_selected)

# Definisce una funzione per la selezione del file di output
def select_output_file():
    file_selected = filedialog.asksaveasfilename(filetypes=[("cbz file", ".cbz")], defaultextension=".cbz")
    output_file_entry.delete(0, tk.END)
    output_file_entry.insert(0, file_selected)

#root.title("undefined")
width=592
height=424

#setting window size
window = tk.Tk()
window.title("Comrpimi cbr/cbz singolo")
window.geometry('%dx%d' % (width, height))
window.resizable(width=False, height=False)
screenwidth = window.winfo_screenwidth()
screenheight = window.winfo_screenheight()

alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
window.geometry(alignstr)

# Crea i widget per la selezione del file di input
input_file_label = tk.Label(window, text="Seleziona il file cbr/cbz da comprimere")
input_file_label.place(x=10,y=0,height=30)
input_file_entry = tk.Entry(window)
input_file_entry.place(x=10,y=30,width=486,height=30)
input_file_button = tk.Button(window, text="Sfoglia", command=select_input_file)
input_file_button.place(x=510,y=30,width=70,height=30)

# Crea i widget per la selezione del file di output
output_file_label = tk.Label(window, text="Scegli il nome del file cbz compresso")
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

output_message = tk.Entry(window)
output_message.place(x=30,y=270,width=530,height=131)
output_message.configure(state='disabled')
print(output_message.cget('state'))

# Crea i widget per la selezione delle radiobox
radio_var = tk.IntVar()
radio1 = tk.Radiobutton(window, variable=radio_var, value=1)
radio1.place(x=380,y=170,width=85,height=25)

radio2 = tk.Radiobutton(window, variable=radio_var, value=2)
radio2.place(x=450,y=170,width=85,height=25)

radio3 = tk.Radiobutton(window, variable=radio_var, value=3)
radio3.place(x=520,y=170,width=85,height=25)

# Crea il widget per il pulsante di conferma
confirm_button = tk.Button(window, text="AVVIA", command=window.quit)
confirm_button.place(x=250,y=220,width=110,height=30)

# Avvia il loop principale della GUI
window.mainloop()