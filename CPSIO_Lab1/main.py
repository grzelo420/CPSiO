import tkinter as tk
from tkinter import filedialog, Entry, Button, messagebox, Label, Frame
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class EkgViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.ax = None
        self.signal60 = None
        self.freq2 = None
        self.samples = None
        self.t = None
        self.signal = None
        self.duration = None
        self.sample_rate = 360
        self.freq = None
        self.control_frame = None
        self.canvas_widget = None
        self.figure = None
        self.canvas = None
        self.end_entry = None
        self.start_entry = None
        self.freq_entry = None
        self.title("EKG Viewer")
        self.geometry("1000x800")
        self.data = None
        self.fs = 360  # Default sampling frequency
        self.create_widgets()

    def create_widgets(self):
        control_frame = Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        Button(control_frame, text="Load EKG Data", command=self.load_data).pack(side=tk.LEFT, padx=5)
        #Button(self.control_frame, text="Pokaż FFT sygnału sinusoidalnego", command=self.generate_and_plot_fft).pack(
         #   side=tk.LEFT, padx=5)
        #Label(control_frame, text="sample rate [Hz]:").pack(side=tk.LEFT, padx=5)
        #self.sample_rate = Entry(control_frame, width=7)
        #self.sample_rate.insert(0,"360")
        #self.sample_rate.pack(side=tk.LEFT, padx=5)

        Label(control_frame, text="Frequency [Hz]:").pack(side=tk.LEFT, padx=5)
        self.freq_entry = Entry(control_frame, width=7)
        self.freq_entry.insert(0, "360")  # Default value for frequency
        self.freq_entry.pack(side=tk.LEFT, padx=5)

        Label(control_frame, text="Start Time [s]:").pack(side=tk.LEFT, padx=5)
        self.start_entry = Entry(control_frame, width=7)
        self.start_entry.pack(side=tk.LEFT, padx=5)

        Label(control_frame, text="End Time [s]:").pack(side=tk.LEFT, padx=5)
        self.end_entry = Entry(control_frame, width=7)
        self.end_entry.pack(side=tk.LEFT, padx=5)

        Button(control_frame, text="Show EKG", command=self.plot_data).pack(side=tk.LEFT, padx=5)
        Button(control_frame, text="Save to File", command=self.save_data).pack(side=tk.LEFT, padx=5)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def load_data(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                self.data = np.loadtxt(file_path)
                # Detect the sampling frequency based on the file name
                if 'ekg1' in file_path:
                    self.fs = 1000
                elif 'ekg100' in file_path or 'ekg_noise' in file_path:
                    self.fs = 360
                # Update the frequency entry with the detected value
                self.freq_entry.delete(0, tk.END)
                self.freq_entry.insert(0, str(self.fs))
                messagebox.showinfo("Data Loaded", f"Data loaded successfully from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {e}")

    def save_data(self):
        if self.data is None:
            messagebox.showerror("Error", "No data to save. Please load EKG data first.")
            return

        # Otwieranie okna dialogowego do zapisu pliku
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            # Anulowanie zapisu, jeśli użytkownik nie poda nazwy pliku
            return

        try:
            start_time = float(self.start_entry.get()) if self.start_entry.get() else 0
            end_time = float(self.end_entry.get()) if self.end_entry.get() else np.max(self.data[:, 0]) / self.fs

            start_index = int(start_time * self.fs)
            end_index = int(end_time * self.fs)

            # Zapisywanie danych do pliku
            if self.data.ndim == 1:
                # Jeden sygnał EKG
                np.savetxt(file_path, self.data[start_index:end_index], delimiter=',')
            else:
                # Wiele sygnałów EKG
                np.savetxt(file_path, self.data[start_index:end_index, :], delimiter=',')

            messagebox.showinfo("Success", f"Data successfully saved to {file_path}")
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid start/end time.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")

    def plot_data(self):
        try:
            start_time = float(self.start_entry.get()) if self.start_entry.get() else 0
            end_time = float(self.end_entry.get()) if self.end_entry.get() else np.max(self.data[:, 0]) / self.fs

            # Obliczenie indeksów na podstawie czasu i częstotliwości próbkowania
            start_index = int(start_time * self.fs)
            end_index = int(end_time * self.fs)

            self.ax.clear()
            if self.data.ndim == 1:
                # Jeden sygnał EKG
                self.ax.plot(self.data[start_index:end_index])
            else:
                # Wiele sygnałów EKG
                for i in range(self.data.shape[1]):
                    self.ax.plot(self.data[start_index:end_index, i], label=f'Channel {i + 1}')

            self.ax.set_title('EKG Signal')
            self.ax.set_xlabel('Sample Index')
            self.ax.set_ylabel('Amplitude')
            if self.data.ndim > 1:
                self.ax.legend()
            self.canvas.draw()
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid start/end time.")

    def generate_sine_wave(self):
        # Ustawienia fali sinusoidalnej
        self.freq = 50  # Częstotliwość fali sinusoidalnej [Hz]
        self.sample_rate = 360  # Częstotliwość próbkowania [Hz]
        self.duration = 1  # Czas trwania sygnału [s]
        self.samples = int(self.sample_rate * self.duration)  # Liczba próbek
        self.t = np.linspace(0, self.duration, self.samples, endpoint=False)
        self.signal = np.sin(2 * np.pi * self.freq * self.t)
        self.plot_signal(self.signal, self.t, "Sygnał sinusoidalny")

    def generate_mixed_sine_wave(self):
        # Ustawienia fali sinusoidalnej
        freq1 = 50  # Częstotliwość pierwszej fali sinusoidalnej [Hz]
        freq2 = 60  # Częstotliwość drugiej fali sinusoidalnej [Hz]
        sample_rate = 360  # Częstotliwość próbkowania [Hz]
        duration = 1  # Czas trwania sygnału [s]
        samples = int(sample_rate * duration)  # Liczba próbek
        t = np.linspace(0, duration, samples, endpoint=False)
        signal1 = np.sin(2 * np.pi * freq1 * t)
        signal2 = np.sin(2 * np.pi * freq2 * t)

        self.signal = signal1 + signal2
        # Wyświetlanie obu sygnałów na wykresie
        self.ax.clear()
        self.ax.plot(t, self.signal, label='50 Hz', color='blue')
        #self.ax.plot(t, signal2, label='60 Hz', color='red')
        self.ax.set_title('Mieszana fala sinusoidalna')
        self.ax.set_xlabel('Czas [s]')
        self.ax.set_ylabel('Amplituda')
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()

    def plot_signal(self, signal, time, title):
        self.ax.clear()
        self.ax.plot(time, signal)
        self.ax.set_title(title)
        self.ax.set_xlabel('Czas [s]')
        self.ax.set_ylabel('Amplituda')
        self.ax.grid(True)
        self.canvas.draw()

    def perform_fft(self):
        fft_result = np.fft.rfft(self.signal)
        fft_freq = np.fft.rfftfreq(len(self.signal), 1 / self.sample_rate)
        self.signal = fft_result
        self.ax.clear()
        self.ax.plot(fft_freq, np.abs(self.signal))
        self.ax.set_title('Widmo amplitudowe')
        self.ax.set_xlabel('Częstotliwość [Hz]')
        self.ax.set_ylabel('Amplituda')
        self.canvas.draw()

    def generate_and_plot_fft(self):
        freq = 50  # Frequency of the sine wave
        sample_rate = 360  # Sampling rate
        duration = 65536 / sample_rate
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        signal = np.sin(2 * np.pi * freq * t)
        fft_result = np.fft.rfft(signal)
        fft_freq = np.fft.rfftfreq(len(signal), 1 / sample_rate)
        self.ax.clear()
        self.ax.plot(fft_freq, np.abs(fft_result))
        self.ax.set_title('Widmo amplitudowe sygnału sinusoidalnego')
        self.ax.set_xlabel('Częstotliwość [Hz]')
        self.ax.set_ylabel('Amplituda')
        self.canvas.draw()

    def generate_and_plot_mixed_signal_fft(self):
        # Frequencies for the mixed signal
        freq1 = 50
        freq2 = 60
        sample_rate = 360  # Sampling rate
        duration = 65536 / sample_rate
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        signal = np.sin(2 * np.pi * freq1 * t) + np.sin(2 * np.pi * freq2 * t)
        fft_result = np.fft.rfft(signal)
        fft_freq = np.fft.rfftfreq(len(signal), 1 / sample_rate)

        self.ax.clear()
        self.ax.plot(fft_freq, np.abs(fft_result))
        self.ax.set_title('Widmo amplitudowe mieszanej fali sinusoidalnej')
        self.ax.set_xlabel('Częstotliwość [Hz]')
        self.ax.set_ylabel('Amplituda')
        self.canvas.draw()

    def plot_inverse_fft(self):
        # Calculate Inverse FFT
        ifft_result = np.fft.irfft(self.signal)

        # Plot original signal
        self.ax.clear()
        self.ax.plot(ifft_result)
        self.ax.set_title('Sygnał po odwrotnej transformacie Fouriera')
        self.ax.set_xlabel('Indeks próbki')
        self.ax.set_ylabel('Amplituda')
        self.canvas.draw()


if __name__ == "__main__":
    app = EkgViewer()
    #Button(app.control_frame, text="FFT sygnału 50 Hz", command=app.generate_and_plot_fft).pack(side=tk.LEFT)

    Button(app.control_frame, text="FFT mieszanej fali 50 i 60 Hz",
           command=app.generate_and_plot_mixed_signal_fft).pack(side=tk.LEFT)
    # Przycisk do generowania i wyświetlania sygnału sinusoidalnego
    Button(app.control_frame, text="Generuj falę sinusoidalną", command=app.generate_sine_wave).pack(side=tk.LEFT)
    Button(app.control_frame, text="Generuj mieszana falę sinusoidalną", command=app.generate_mixed_sine_wave).pack(side=tk.LEFT)
    # Przyciski do wykonania FFT na wygenerowanym sygnale
    Button(app.control_frame, text="Wykonaj FFT", command=app.perform_fft).pack(side=tk.LEFT)
    Button(app.control_frame, text="Odwrotna FFT", command=app.plot_inverse_fft).pack(side=tk.LEFT)
    app.mainloop()
