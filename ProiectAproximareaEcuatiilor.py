import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.integrate import odeint
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sympy as sp
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import csv
import random

#variabile globale
data = None
ani = None

# Funcții
def salveaza_animatie():
    cale_fisier = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
    if cale_fisier:
        try:
            Writer = animation.writers['ffmpeg']
            writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
            ani.save(cale_fisier, writer=writer)
            messagebox.showinfo("Succes", "Animatie salvata cu succes.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def citeste_fisier():
    cale_fisier = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if cale_fisier:
        try:
            with open(cale_fisier, 'r') as file:
                lines = file.readlines()

            for line in lines:
                parts = line.strip().split('=')
                if len(parts) == 2:
                    variable = parts[0].strip()
                    value = parts[1].strip()
                    if variable == 'dydt':
                        dydt_entry.delete(0, tk.END)
                        dydt_entry.insert(tk.END, value)
                    elif variable == 'y0':
                        y0_entry.delete(0, tk.END)
                        y0_entry.insert(tk.END, value)
                    elif variable == 't':
                        t_entry.delete(0, tk.END)
                        t_entry.insert(tk.END, value)
            
            valideaza_dydt_intrare()
            valideaza_y0_intrare()
            valideaza_t_intrare()

        except Exception as e:
            messagebox.showerror("Error", str(e))

def input_random():
    dydt_entry.delete(0, tk.END)
    y0_entry.delete(0, tk.END)
    t_entry.delete(0, tk.END)
    dydt_entry.insert(0,generate_random_equation())
    y0_entry.insert(0, random.randint(1,100))
    t_entry.insert(0, random.randint(0, 100))

def generate_random_equation():
    a = random.randint(1, 100)   
    b = random.randint(1, 100)   
    operator = random.choice(['+', '-','/','*'])  
    equation = f"{a}*t {operator} {b}"  
    return equation

def salveaza_csv():
    cale_fisier = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if cale_fisier:
        try:
            dydt_str = 'dy/dt=' + dydt_entry.get()
            with open(cale_fisier, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([dydt_str]) 
                data.to_csv(file, index=False)

            messagebox.showinfo("Succes", "Date salvate cu succes.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def afiseaza_date():
    global data
    # Crearea unei noi ferestre top-level
    data_window = tk.Toplevel(root)
    data_window.title("Tabel Date")

    tree = ttk.Treeview(data_window)
    tree['columns'] = list(data.columns)  # Adăugăm coloanele

    for col in data.columns:
        tree.column(col, width=100)  # Setăm lățimea coloanelor
        tree.heading(col, text=col)  # Setăm denumirea coloanelor

    for i, row in data.iterrows():
        tree.insert("", tk.END, text=i, values=list(row))

    tree.pack(fill="both", expand=True)

    # Butonul pentru salvarea datelor
    btn_salvare = tk.Button(data_window, text="Salveaza Datele", command=salveaza_csv)
    btn_salvare.pack()


def euler(dydt, y0, t):
    y = np.zeros(len(t))
    y[0] = y0

    for i in range(len(t) - 1):
        dt = t[i + 1] - t[i]
        y[i + 1] = y[i] + dydt(y[i], t[i]) * dt

    return y

def runge_kutta(dydt, y0, t):
    y = np.zeros(len(t))
    y[0] = y0

    for i in range(len(t) - 1):
        dt = t[i + 1] - t[i]
        k1 = dydt(y[i], t[i])
        k2 = dydt(y[i] + 0.5 * dt * k1, t[i] + 0.5 * dt)
        k3 = dydt(y[i] + 0.5 * dt * k2, t[i] + 0.5 * dt)
        k4 = dydt(y[i] + dt * k3, t[i] + dt)
        y[i + 1] = y[i] + (1 / 6) * dt * (k1 + 2 * k2 + 2 * k3 + k4)

    return y

def dydt(y, t):
    dydt_str = dydt_entry.get()
    try:
        t_symbol = sp.symbols('t')
        expr = sp.sympify(dydt_str)
        dydt_func = sp.lambdify(t_symbol, expr)
        return dydt_func(t)
    except: 
        return 0

def elibereaza_nevalid(event):
    entry = event.widget
    value = entry.get()
    if value == "Intrare nevalida":
        entry.delete(0, tk.END)
        
def valideaza_dydt_intrare():
    dydt_str = dydt_entry.get()
    try:
        # Verificare expresii
        t_symbol = sp.symbols('t')
        expr = sp.sympify(dydt_str)

        # Verificare variabile permise
        allowed_variables = ['t']
        variables = expr.free_symbols
        for var in variables:
            if str(var) not in allowed_variables:
                raise ValueError('Variabila nevalidă: ' + str(var))

    except (sp.SympifyError, TypeError, ValueError):
        dydt_entry.delete(0, tk.END)
        dydt_entry.insert(tk.END, "Intrare nevalida")
        return
    return True

def valideaza_y0_intrare():
    y0_str = y0_entry.get()
    try:
        float(y0_str)
    except:
        y0_entry.delete(0, tk.END)
        y0_entry.insert(tk.END, "Intrare nevalida")

def valideaza_t_intrare():
    t_str = t_entry.get()
    try:
        t = float(t_str)
        if t <= 0:
            raise ValueError("Intrare nevalida pentru 't'")
    except ValueError:
        t_entry.delete(0, tk.END)
        t_entry.insert(tk.END, "Intrare nevalida")

def calculeaza_valori(dydt, y0, t):
    t_span = np.linspace(0, t, 101)
    
    metoda = metoda_var.get()
    y=0
    if metoda == "euler":
        y = euler(dydt, y0, t_span)
    elif metoda == "runge_kutta":
        y = runge_kutta(dydt, y0, t_span)
    else:
        print("Error:", "Metoda nevalida.")

    y_odeint = odeint(dydt, y0, t_span).flatten()
    abs_error = calculeaza_er_abs(y_odeint, y)
    rel_error = calculeaza_er_rel(y_odeint, y)

    data = pd.DataFrame({'t': t_span, 'y_odeint': y_odeint, 'y-metoda': y, 'abs_error': abs_error, 'rel_error': rel_error})
    return data

def update_plot(i):
    global data
    
    #dydt_str = dydt_entry.get()
    y0_str = y0_entry.get()
    t_str = t_entry.get()
    
    y0 = float(y0_str)
    t = float(t_str)
    
    t_span = np.linspace(0, t, 101)
    #y0_arr = np.array([y0])

    metoda = metoda_var.get()
    y=0
    if metoda == "euler":
        y = euler(dydt, y0, t_span)
    elif metoda == "runge_kutta":
        y = runge_kutta(dydt, y0, t_span)
    else:
        print("Error:", "Invalid metoda.")

    y_odeint = odeint(dydt, y0, t_span).flatten()
    abs_error = calculeaza_er_abs(y_odeint, y) 
    rel_error = calculeaza_er_rel(y_odeint, y)
    data = calculeaza_valori(dydt, y0, t)
    
    ax.clear()
    ax.set_xlim(0, t*1.1)
    ax.set_ylim(min(y) - 0.1 * abs(min(y)), max(y) + 0.1 * abs(max(y)))
    ax.plot(t_span[:i], y[:i])
    ax.set_xlabel("t")
    ax.set_ylabel("y")

    abs_error_value.config(text=str(abs_error[min(i, len(abs_error)-1)]))
    if isinstance(rel_error, np.ndarray) and i < len(rel_error):
        rel_error_value.config(text=str(rel_error[min(i, len(rel_error)-1)]))
    
    return ax.plot(t_span[:i], y[:i])

def calculeaza_er_abs(y1, y2):
    return np.abs(y1 - y2)

def calculeaza_er_rel(y1, y2):
    abs_error = calculeaza_er_abs(y1, y2)
    abs_y1 = np.abs(y1)
    rel_error = np.zeros_like(abs_y1)

    nonzero_indices = abs_y1 != 0
    rel_error[nonzero_indices] = abs_error[nonzero_indices] / abs_y1[nonzero_indices] # folosim astfel pentru evitarea impartirii la 0

    return rel_error

def start_animatie():
    
    if dydt_entry.get() == "" or y0_entry.get() == "" or t_entry.get() == "" or dydt_entry.get() == "Intrare nevalida" or y0_entry.get() == "Intrare nevalida" or t_entry.get() == "Intrare nevalida":
        messagebox.showerror("Eroare", "Aveti erori in campurile de intrare!")
        return
    
    btn_start.config(state='disabled')
    btn_citeste_fisier.config(state='disabled')
    btn_random.config(state='disabled')
    btn_reset.config(state='normal')
    btn_afiseaza_tabel.config(state='normal')  
    btn_salvare.config(state='normal')  
    euler_radio.config(state='disabled')  
    runge_kutta_radio.config(state='disabled') 
    
    t_entry.config(state='disabled') 
    y0_entry.config(state='disabled')  
    dydt_entry.config(state='disabled')
    
    global ani
    ani = animation.FuncAnimation(fig, update_plot, interval=100, blit=True)
    canvas.draw()
    
def stop_animatie():
    ani.event_source.stop()

def reset_plot():
    stop_animatie()

    ax.clear()
    canvas.draw()
    
    t_entry.config(state='normal')  
    y0_entry.config(state='normal')  
    dydt_entry.config(state='normal')  
    
    dydt_entry.delete(0, tk.END)
    y0_entry.delete(0, tk.END)
    t_entry.delete(0, tk.END)
fz
    abs_error_value.config(text="")
    rel_error_value.config(text="")
    
    btn_start.config(state='normal')  
    btn_citeste_fisier.config(state='normal')
    btn_random.config(state='normal')
    btn_reset.config(state='disabled')  
    btn_afiseaza_tabel.config(state='disabled')  
    btn_salvare.config(state='disabled') 
    euler_radio.config(state='normal') 
    runge_kutta_radio.config(state='normal')  
    
    global ani
    ani = None

    canvas.draw()
    
root = tk.Tk()
root.title("Ecuatii diferentiale ordinale")
root.configure(bg='#F5F5DC')

btn_afiseaza_tabel = tk.Button(root, text="Deschide tabelul", command=afiseaza_date, state='disabled')
btn_afiseaza_tabel.grid(row=0, column=3, columnspan=2, ipadx=5,ipady=5)

# Figura și graficul
fig = plt.figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=1, column=3, rowspan=7, padx=20, pady=10, sticky="nsew")

dydt_label = tk.Label(root, text="dy/dt:", bg='#F5F5DC', fg='#333333')
dydt_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

dydt_entry = tk.Entry(root)
dydt_entry.grid(row=1, column=1, pady=10)
dydt_entry.bind("<FocusOut>", lambda event: valideaza_dydt_intrare())

y0_label = tk.Label(root, text="y0:", bg='#F5F5DC', fg='#333333')
y0_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

y0_entry = tk.Entry(root)
y0_entry.grid(row=2, column=1, padx=10, pady=10)
y0_entry.bind("<FocusOut>", lambda event: valideaza_y0_intrare())

t_label = tk.Label(root, text="t:", bg='#F5F5DC', fg='#333333')
t_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")

t_entry = tk.Entry(root)
t_entry.grid(row=3, column=1, padx=10, pady=10)
t_entry.bind("<FocusOut>", lambda event: valideaza_t_intrare())

dydt_entry.bind("<FocusIn>", elibereaza_nevalid)
y0_entry.bind("<FocusIn>", elibereaza_nevalid)
t_entry.bind("<FocusIn>", elibereaza_nevalid)

# Butonul pentru citire din fișier
btn_citeste_fisier = tk.Button(root, text="Citire din fișier", command=citeste_fisier)
btn_citeste_fisier.grid(row=4, column=1, padx=10, pady=10, ipadx=5,ipady=5,sticky='e')

#Buton random 
btn_random = tk.Button(root, text="Generare random", command=input_random)
btn_random.grid(row=4, column=0, padx=10, pady=5,ipadx=5 ,ipady=5, sticky="e")
# Radiobutoane pentru metoda selectată
metoda_var = tk.StringVar()
metoda_var.set("euler")

euler_radio = tk.Radiobutton(root, text="Metoda Euler", variable=metoda_var, value="euler", bg='#F5F5DC', fg='#333333')
euler_radio.grid(row=5, column=1, padx=10, pady=(0, 5), sticky="nsew")

runge_kutta_radio = tk.Radiobutton(root, text="Metoda Runge-Kutta", variable=metoda_var, value="runge_kutta", bg='#F5F5DC', fg='#333333')
runge_kutta_radio.grid(row=6, column=1, padx=10, pady=(5, 0), sticky="nsew")

box_style = { "borderwidth": 1, "relief": "solid"}

abs_error_frame = tk.Frame(root, bg='#F5F5DC', **box_style)
abs_error_frame.grid(row=7, column=0, padx=10, pady=5, sticky="e")
abs_error_label = tk.Label(abs_error_frame, text="Absolute Error: ", fg='#333333')
abs_error_label.pack(padx=5, pady=5)

abs_error_value_frame = tk.Frame(root, width=200, height=30, bg='#F5F5DC', **box_style)
abs_error_value_frame.grid(row=7, column=1, padx=20, pady=5, sticky="w")
abs_error_value_frame.pack_propagate(0)
abs_error_value = tk.Label(abs_error_value_frame, text="", fg='#333333')
abs_error_value.pack(fill="both", padx=5, pady=5)

rel_error_frame = tk.Frame(root, bg='#F5F5DC', **box_style)
rel_error_frame.grid(row=8, column=0, padx=10, pady=5, sticky="e")
rel_error_label = tk.Label(rel_error_frame, text="Relative Error: ", fg='#333333')
rel_error_label.pack(padx=5, pady=5)

rel_error_value_frame = tk.Frame(root, width=200, height=30, bg='#F5F5DC', **box_style)
rel_error_value_frame.grid(row=8, column=1, padx=20, pady=5, sticky="w")
rel_error_value_frame.pack_propagate(0)
rel_error_value = tk.Label(rel_error_value_frame, text="", fg='#333333')
rel_error_value.pack(fill="both", padx=5, pady=5)

# Butonul pentru salvarea animației
btn_salvare = tk.Button(root, text="Salvează animația", command=salveaza_animatie, state='disabled')
btn_salvare.grid(row=8, column=3, padx=20, pady=10,ipadx=5,ipady=5, sticky="w")

# Butonul pentru resetarea plotului și valorilor de intrare
btn_reset = tk.Button(root, text="Reset", command=reset_plot, state='disabled')
btn_reset.grid(row=8, column=3, padx=20, pady=10,ipadx=5,ipady=5, sticky="e")

# Butonul pentru start animație
btn_start = tk.Button(root, text="Start Animation", command=start_animatie)
btn_start.grid(row=10, column=1, padx=10, pady=10, ipadx=5,ipady=5)

root.mainloop()