import tkinter as tk
from tkinter import ttk, messagebox
import requests
import subprocess
import threading
import os
import signal
import json
from tkinter import BooleanVar

class EndpointManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Endpoint Manager")
        self.root.geometry("700x600+200+50")
        self.root.configure(bg="#f4f4f4")

        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 10), padding=6)
        self.style.configure("TLabel", font=("Arial", 12), background="#f4f4f4")

        header_frame = tk.Frame(root, bg="#f4f4f4")
        header_frame.pack(pady=10, fill=tk.X)
        title_label = tk.Label(header_frame, text="Endpoint Manager", font=("Arial", 20, "bold"), bg="#f4f4f4", fg="#333")
        title_label.pack(side=tk.LEFT, padx=10)
        self.server_status_label = tk.Label(header_frame, text="Servidor: Inativo", font=("Arial", 12, "bold"), bg="#f4f4f4", fg="#dc3545")
        self.server_status_label.pack(side=tk.RIGHT, padx=10)

        base_url_frame = tk.Frame(root, bg="#f4f4f4")
        base_url_frame.pack(pady=5, fill=tk.X, padx=20)
        base_url_label = tk.Label(base_url_frame, text="Base URL:", bg="#f4f4f4", font=("Arial", 12))
        base_url_label.pack(side=tk.LEFT)
        self.base_url_entry = tk.Entry(base_url_frame, width=40, font=("Arial", 10))
        self.base_url_entry.insert(0, "http://127.0.0.1:8000")
        self.base_url_entry.pack(side=tk.LEFT, padx=10)

        main_frame = tk.Frame(root, bg="#f4f4f4")
        main_frame.pack(pady=5, fill=tk.BOTH, expand=True, padx=20)

        endpoint_frame = tk.Frame(main_frame, bg="#f4f4f4", relief=tk.GROOVE, bd=2)
        endpoint_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        endpoint_label = tk.Label(endpoint_frame, text="Endpoints", bg="#f4f4f4", font=("Arial", 12, "bold"))
        endpoint_label.pack(pady=5)
        self.endpoint_listbox = tk.Listbox(endpoint_frame, height=8, selectmode=tk.SINGLE, font=("Arial", 10))
        self.endpoint_listbox.pack(pady=5, fill=tk.BOTH, expand=True)
        self.endpoints = self.get_api_paths()
        for endpoint in self.endpoints:
            self.endpoint_listbox.insert(tk.END, endpoint.replace("/", "").upper())

        auth_frame = tk.Frame(main_frame, bg="#f4f4f4", relief=tk.GROOVE, bd=2)
        auth_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        auth_label = tk.Label(auth_frame, text="Gerenciar Autorização", bg="#f4f4f4", font=("Arial", 12, "bold"))
        auth_label.pack(pady=5)

        self.auth_items_frame = tk.Frame(auth_frame, bg="#f4f4f4")
        self.auth_items_frame.pack(pady=5, fill=tk.BOTH, expand=True)

        self.auth_scrollbar = tk.Scrollbar(self.auth_items_frame, orient=tk.VERTICAL)
        self.auth_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.auth_canvas = tk.Canvas(self.auth_items_frame, bg="#f4f4f4", yscrollcommand=self.auth_scrollbar.set, highlightthickness=0)
        self.auth_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.auth_inner_frame = tk.Frame(self.auth_canvas, bg="#f4f4f4")
        self.auth_canvas.create_window((0, 0), window=self.auth_inner_frame, anchor="nw")

        self.auth_scrollbar.config(command=self.auth_canvas.yview)
        self.auth_inner_frame.bind("<Configure>", lambda e: self.auth_canvas.configure(scrollregion=self.auth_canvas.bbox("all")))

        self.refresh_button = tk.Button(
            auth_frame, text="Atualizar", command=self.load_auth_data, bg="#0078D7", fg="white", font=("Arial", 10), relief=tk.FLAT
        )
        self.refresh_button.pack(pady=5)

        self.auth_data = []
        self.auth_checkbuttons = []
        self.load_auth_data()

        button_frame = tk.Frame(root, bg="#f4f4f4")
        button_frame.pack(pady=10)
        self.fetch_button = tk.Button(button_frame, text="Buscar", command=self.fetch_data, bg="#0078D7", fg="white", font=("Arial", 10), relief=tk.FLAT)
        self.fetch_button.grid(row=0, column=0, padx=5)
        self.update_server_status(self.check_server_status())
        result_frame = tk.Frame(root, bg="#f4f4f4")
        result_frame.pack(pady=5, fill=tk.BOTH, expand=True, padx=20)
        self.result_text = tk.Text(result_frame, height=10, wrap=tk.WORD, font=("Arial", 10), relief=tk.FLAT)
        self.result_text.pack(pady=5, fill=tk.BOTH, expand=True)

        self.server_process = None

    def update_server_status(self, active):
        if active:
            self.server_status_label.config(text="Servidor: Ativo", fg="#28a745")
        else:
            self.server_status_label.config(text="Servidor: Inativo", fg="#dc3545")

    def fetch_data(self):
        selected = self.endpoint_listbox.curselection()
        if not selected:
            messagebox.showwarning("Aviso", "Por favor, selecione um endpoint.")
            return

        endpoint = self.endpoint_listbox.get(selected[0])
        base_url = self.base_url_entry.get().strip()
        url = base_url + "/" + endpoint.lower()
        headers={"nome": "Admin"}
        try:
            response = requests.get(url,headers=headers)
            if response.status_code == 200:
                data = response.json()
                data_length = len(data) if isinstance(data, list) else 1
                truncated_data = str(data)[:100] + ("..." if len(str(data)) > 100 else "")
                
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, f"Endpoint: {endpoint}\n")
                self.result_text.insert(tk.END, f"Total Records: {data_length}\n")
                self.result_text.insert(tk.END, f"Data Preview (max 100 chars):\n{truncated_data}\n")
                self.update_server_status(True)
                return
            else:
                messagebox.showerror("Erro", f"Falha ao buscar dados. Código de status: {response.status_code}.\n {response.json()['detail']}")
                return
        except Exception as e:
            vamo=self.check_server_status()
            self.update_server_status(vamo)
            if not vamo:
                messagebox.showwarning("Aviso", "Por favor, inicie o servidor.")
                return
            else:
                print(f"Erro ao buscar dados: {e}")
                messagebox.showerror("Erro", f"Erro ao buscar dados: {e}")
                return
    def start_server(self):
        """Start server functionality removed."""
        pass

    def stop_server(self):
        """Stop server functionality removed."""
        pass
    def get_api_paths(self):
        try:
            response = requests.get('http://localhost:8000/openapi.json')
            if response.status_code == 200:
                openapi_data = response.json()
                paths = openapi_data.get("paths", {})
                get_paths = [path for path, methods in paths.items() if "get" in methods]
                return get_paths
            else:
                print(f"Erro ao obter os caminhos da API. Código de status: {response.status_code}")
                return []
        except Exception as e:
            print(f"Erro ao obter os caminhos da API: {e}")
            return []
    def check_server_status(self):
        try:
            response = requests.get('http://localhost:8000/docs')
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            print(f"Erro ao verificar o status do servidor: {e}")
            return False
    
    def monitor_server_output(self):
        while self.server_process and self.server_process.poll() is None:
            output = self.server_process.stdout.readline()
            if output:
                self.result_text.insert(tk.END, output.decode("utf-8"))
                self.result_text.see(tk.END)

    def load_auth_data(self):
        """Load names from autorizador.json into the dynamic list with checkboxes and color coding."""
        for widget in self.auth_inner_frame.winfo_children():
            widget.destroy()

        file_path = "autorizador.json"
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                self.auth_data = json.load(file)

            self.auth_checkbuttons = []
            for entry in self.auth_data:
                var = BooleanVar(value=entry["status"])
                frame = tk.Frame(self.auth_inner_frame, bg="#f4f4f4")
                frame.pack(fill=tk.X, pady=2)

                checkbutton = tk.Checkbutton(
                    frame,
                    text=entry["nome"],
                    variable=var,
                    bg="#f4f4f4",
                    font=("Arial", 10),
                    command=lambda e=entry, v=var: self.update_item_color(e, v),
                )
                checkbutton.pack(side=tk.LEFT, anchor="w", padx=5)

                self.update_item_color(entry, var)

                self.auth_checkbuttons.append((entry, var))

    def update_item_color(self, entry, var):
        """Update the color of the checkbox text based on its status."""
        status = var.get()
        entry["status"] = status
        color = "green" if status else "red"
        for widget in self.auth_inner_frame.winfo_children():
            children = widget.winfo_children()
            if children and isinstance(children[0], tk.Checkbutton):
                if children[0].cget("text") == entry["nome"]:
                    children[0].config(fg=color)
        self.save_auth_data(entry)

    def save_auth_data(self, updated_entry):
        """Update the status of a specific entry in autorizador.json."""
        file_path = "autorizador.json"
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
            else:
                data = []

            for entry in data:
                if entry["nome"] == updated_entry["nome"]:
                    entry["status"] = updated_entry["status"]
                    break

            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar os dados de autorização: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EndpointManagerApp(root)
    root.mainloop()
