import tkinter as tk
from tkinter import ttk
import numpy as np

from tx import cdma_transmitter
from rx import cdma_receiver

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sistema CDMA")
        self.geometry("1000x700")

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.frames = {}

        for F in (MainMenu, TXScreen, RXScreen):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainMenu)

        # Variables compartidas
        self.data = None
        self.codes = None
        self.all_signals = None
        self.combined_signal = None
        self.recovered = None
        self.users = 0
        self.num_bits = 0

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# MENU PRINCIPAL

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        ttk.Label(self, text="Modulador/Demodulador CDMA", font=("Arial", 18)).pack(pady=20)

        ttk.Label(self, text="Número de usuarios:").pack()
        self.users_entry = ttk.Entry(self)
        self.users_entry.pack()

        ttk.Label(self, text="Bits por usuario:").pack()
        self.bits_entry = ttk.Entry(self)
        self.bits_entry.pack()

        ttk.Button(self, text="TX", command=self.go_tx).pack(pady=15)
        ttk.Button(self, text="RX", command=self.go_rx).pack(pady=15)
        ttk.Button(self, text="Salir", command=controller.destroy).pack(pady=10)

    def go_tx(self):
        self.get_inputs()
        self.controller.show_frame(TXScreen)

    def go_rx(self):
        self.get_inputs()
        self.controller.show_frame(RXScreen)

    def get_inputs(self):
        self.controller.users = int(self.users_entry.get())
        self.controller.num_bits = int(self.bits_entry.get())

# PANTALLA TX

class TXScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        ttk.Label(self, text="Transmisor (TX)", font=("Arial", 16)).pack(pady=10)

        self.text = tk.Text(self, height=12)
        self.text.pack(fill="x")

        ttk.Button(self, text="Ejecutar TX", command=self.run_tx).pack(pady=10)
        ttk.Button(self, text="Volver", command=lambda: controller.show_frame(MainMenu)).pack()

        # Scroll container
        #self.container = tk.Frame(self)
        #self.container.pack(fill="both", expand=True)
        self.container = tk.Frame(self, height=700, width=1100)
        self.container.pack(fill="both", expand=True)
        self.container.pack_propagate(False)

        self.canvas = tk.Canvas(self.container)
        self.scrollbar = tk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.plot_canvas = None

    def run_tx(self):

        users = self.controller.users
        num_bits = self.controller.num_bits

        data, codes, all_signals, combined_signal = cdma_transmitter(users, num_bits)

        self.controller.data = data
        self.controller.codes = codes
        self.controller.all_signals = all_signals
        self.controller.combined_signal = combined_signal

        # Mostrar datos
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, f"Datos:\n{data}\n\nCódigos:\n{codes}")

        self.plot_tx(all_signals, combined_signal)

    def plot_tx(self, all_signals, combined_signal):

        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().destroy()

        #fig = Figure(figsize=(6, 2.5*(len(all_signals)+1)), dpi=100)
        fig = Figure(figsize=(10, 2.5*(len(all_signals)+1)), dpi=100)

        for i, signal in enumerate(all_signals):
            ax = fig.add_subplot(len(all_signals)+1, 1, i+1)

            x = np.arange(len(signal) + 1)
            y = np.append(signal, signal[-1])

            ax.step(x, y, where='post')
            ax.set_xlim(0, len(signal))
            ax.set_ylim(-1.5, 1.5)
            ax.set_title(f'Usuario {i+1}')
            ax.grid()

        ax = fig.add_subplot(len(all_signals)+1, 1, len(all_signals)+1)

        x = np.arange(len(combined_signal) + 1)
        y = np.append(combined_signal, combined_signal[-1])

        ax.step(x, y, where='post')
        ax.set_xlim(0, len(combined_signal))
        ax.set_title("Señal Combinada")
        ax.grid()

        fig.tight_layout(pad=2.0)

        self.plot_canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().pack(fill="both", expand=True)


# PANTALLA RX

class RXScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        ttk.Label(self, text="Receptor (RX)", font=("Arial", 16)).pack(pady=10)

        self.text = tk.Text(self, height=6)
        self.text.pack(fill="x")

        ttk.Button(self, text="Ejecutar RX", command=self.run_rx).pack(pady=10)
        ttk.Button(self, text="Volver", command=lambda: controller.show_frame(MainMenu)).pack()

        # Scroll container
        #self.container = tk.Frame(self)
        #self.container.pack(fill="both", expand=True)
        self.container = tk.Frame(self, height=700, width=1100)
        self.container.pack(fill="both", expand=True)
        self.container.pack_propagate(False)

        self.canvas = tk.Canvas(self.container)
        self.scrollbar = tk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.plot_canvas = None

    def run_rx(self):

        if self.controller.combined_signal is None:
            self.text.insert(tk.END, "Primero ejecuta TX\n")
            return

        recovered = cdma_receiver(
            self.controller.combined_signal,
            self.controller.codes,
            self.controller.num_bits
        )

        self.controller.recovered = recovered

        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, f"Recuperados:\n{recovered}")

        self.plot_rx(recovered)

    def plot_rx(self, recovered_data):

        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().destroy()

        #fig = Figure(figsize=(6, 2.5*len(recovered_data)), dpi=100)
        fig = Figure(figsize=(10, 2.5*len(recovered_data)), dpi=100)

        for i, bits in enumerate(recovered_data):
            ax = fig.add_subplot(len(recovered_data), 1, i+1)

            x = np.arange(len(bits) + 1)
            y = np.append(bits, bits[-1])

            ax.step(x, y, where='post')
            ax.set_xlim(0, len(bits))
            ax.set_ylim(-0.5, 1.5)
            ax.set_title(f'Usuario {i+1}')
            ax.grid()

        fig.tight_layout(pad=2.0)

        self.plot_canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().pack(fill="both", expand=True)


# MAIN

if __name__ == "__main__":
    app = App()
    app.mainloop()