# Módulo de Autenticação

import ttkbootstrap as ttk
from tkinter import messagebox
from modules.models.database import create_connection
import hashlib


class AuthSystem:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.conn = create_connection()
        self.create_login_window()

    def create_login_window(self):
        """Cria a janela de login"""
        self.login_window = ttk.Toplevel(self.root)
        self.login_window.title("Login - Sistema de Aluguel")
        self.login_window.geometry("400x300")
        self.login_window.resizable(False, False)

        # Centralizar na tela
        window_width = self.login_window.winfo_reqwidth()
        window_height = self.login_window.winfo_reqheight()
        position_right = int(self.login_window.winfo_screenwidth() / 2 - window_width / 2)
        position_down = int(self.login_window.winfo_screenheight() / 2 - window_height / 2)
        self.login_window.geometry(f"+{position_right}+{position_down}")

        # Frame principal
        main_frame = ttk.Frame(self.login_window)
        main_frame.pack(pady=40, padx=20, fill="both", expand=True)

        # Logo/Title
        ttk.Label(
            main_frame,
            text="Sistema de Gestão de Aluguel",
            font=('Helvetica', 14, 'bold')
        ).pack(pady=(0, 20))

        # Formulário de login
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="x")

        ttk.Label(form_frame, text="Usuário:").pack(anchor="w", pady=(5, 0))
        self.username_entry = ttk.Entry(form_frame)
        self.username_entry.pack(fill="x", pady=5)

        ttk.Label(form_frame, text="Senha:").pack(anchor="w", pady=(5, 0))
        self.password_entry = ttk.Entry(form_frame, show="*")
        self.password_entry.pack(fill="x", pady=5)

        # Botão de login
        login_btn = ttk.Button(
            main_frame,
            text="Entrar",
            bootstyle="success",
            command=self.authenticate,
            width=10
        )
        login_btn.pack(pady=20)

        # Focar no campo de usuário
        self.username_entry.focus_set()

        # Bind Enter key to login
        self.password_entry.bind('<Return>', lambda e: self.authenticate())

    def hash_password(self, password):
        """Cria hash da senha usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self):
        """Autentica o usuário"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Erro", "Preencha usuário e senha!")
            return

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, nome, is_admin FROM funcionarios WHERE usuario = ? AND senha = ?",
            (username, self.hash_password(password))
        )
        user = cursor.fetchone()

        if user:
            user_data = {
                'id': user[0],
                'nome': user[1],
                'is_admin': bool(user[2])
            }
            self.login_window.destroy()
            self.on_login_success(user_data)
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos!")

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()