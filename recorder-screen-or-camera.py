# pip install tkinter pygetwindow pyautogui opencv-python
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox
import pygetwindow as gw
import pyautogui
import cv2
import numpy as np
import threading

class ScreenRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Recorder")

        self.label = tk.Label(root, text="Escolha a fonte de gravação:")
        self.label.pack(pady=10)

        self.source_var = tk.StringVar(value="camera")
        self.camera_radiobutton = tk.Radiobutton(root, text="Câmera USB", variable=self.source_var, value="camera")
        self.camera_radiobutton.pack(pady=5)
        self.window_radiobutton = tk.Radiobutton(root, text="Janela", variable=self.source_var, value="window")
        self.window_radiobutton.pack(pady=5)

        self.window_listbox = tk.Listbox(root)
        self.window_listbox.pack(pady=10)

        self.refresh_button = tk.Button(root, text="Atualizar Janelas", command=self.refresh_windows)
        self.refresh_button.pack(pady=5)

        self.select_file_button = tk.Button(root, text="Escolher Local e Nome do Arquivo", command=self.select_file)
        self.select_file_button.pack(pady=5)

        self.record_button = tk.Button(root, text="Gravar", command=self.start_recording)
        self.record_button.pack(pady=20)

        self.stop_button = tk.Button(root, text="Parar Gravação", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.exit_button = tk.Button(root, text="Sair", command=root.quit)
        self.exit_button.pack(pady=5)

        self.file_path = ""
        self.recording = False

        self.windows = []
        self.refresh_windows()

    def refresh_windows(self):
        self.window_listbox.delete(0, tk.END)
        self.windows = gw.getWindowsWithTitle('')
        for window in self.windows:
            self.window_listbox.insert(tk.END, window.title)

    def select_file(self):
        self.file_path = filedialog.asksaveasfilename(defaultextension=".avi", filetypes=[("Video files", "*.avi")])
        if self.file_path:
            messagebox.showinfo("Info", f"Arquivo selecionado: {self.file_path}")

    def start_recording(self):
        if self.source_var.get() == "window":
            selected_index = self.window_listbox.curselection()
            if not selected_index:
                messagebox.showwarning("Aviso", "Por favor, selecione uma janela para gravar.")
                return
        if not self.file_path:
            messagebox.showwarning("Aviso", "Por favor, selecione o local e nome do arquivo.")
            return

        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.exit_button.config(state=tk.DISABLED)

        if self.source_var.get() == "camera":
            self.recording = True
            threading.Thread(target=self.record_camera, args=(self.file_path,)).start()
        else:
            selected_window = self.windows[self.window_listbox.curselection()[0]]
            window_box = selected_window.box
            self.recording = True
            threading.Thread(target=self.record_video, args=(window_box, self.file_path)).start()

    def stop_recording(self):
        self.recording = False
        self.record_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.exit_button.config(state=tk.NORMAL)

    def record_video(self, window_box, file_path):
        x, y, w, h = window_box
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(file_path, fourcc, 20.0, (w, h))

        try:
            while self.recording:
                img = pyautogui.screenshot(region=(x, y, w, h))
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                out.write(frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            out.release()
            cv2.destroyAllWindows()
            messagebox.showinfo("Info", "Gravação finalizada.")

    def record_camera(self, file_path):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Erro", "Não foi possível acessar a câmera.")
            self.stop_recording()
            return
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(file_path, fourcc, 20.0, (width, height))

        try:
            while self.recording:
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            messagebox.showinfo("Info", "Gravação finalizada.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorder(root)
    root.mainloop()
