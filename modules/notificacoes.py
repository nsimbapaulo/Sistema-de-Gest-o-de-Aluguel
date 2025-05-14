import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from modules.models.database import create_connection


class NotificacoesModule:
    def __init__(self, parent):
        self.parent = parent
        self.conn = create_connection()
        self.create_widgets()
        self.load_notificacoes()

    def create_widgets(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame de ações
        actions_frame = ttk.Frame(self.main_frame)
        actions_frame.pack(fill="x", pady=(0, 10))

        add_btn = ttk.Button(
            actions_frame,
            text="Nova Notificação",
            bootstyle="success",
            command=self.open_add_notificacao
        )
        add_btn.pack(side="left", padx=5)

        mark_read_btn = ttk.Button(
            actions_frame,
            text="Marcar como Lida",
            bootstyle="info",
            command=self.mark_as_read
        )
        mark_read_btn.pack(side="left", padx=5)

        # Tabela de notificações
        columns = ("id", "titulo", "mensagem", "tipo", "data_criacao", "lida")
        self.tree = ttk.Treeview(
            self.main_frame,
            columns=columns,
            show="headings",
            bootstyle="dark",
            selectmode="browse"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("titulo", text="Título")
        self.tree.heading("mensagem", text="Mensagem")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("data_criacao", text="Data")
        self.tree.heading("lida", text="Status")

        self.tree.column("id", width=50)
        self.tree.column("titulo", width=150)
        self.tree.column("mensagem", width=300)
        self.tree.column("tipo", width=100)
        self.tree.column("data_criacao", width=120)
        self.tree.column("lida", width=80)

        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configurar tags para linhas não lidas
        self.tree.tag_configure('unread', background='#f0f0f0', foreground='black')

    def load_notificacoes(self):
        """Carrega todas as notificações na tabela"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, titulo, mensagem, tipo, data_criacao, lida FROM notificacoes ORDER BY data_criacao DESC")
        rows = cursor.fetchall()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            status = "Lida" if row[5] else "Não lida"
            tags = () if row[5] else ('unread',)
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], status), tags=tags)

    def open_add_notificacao(self):
        """Abre janela para adicionar nova notificação"""
        self.add_window = ttk.Toplevel(self.parent)
        self.add_window.title("Nova Notificação")

        # Formulário
        form_frame = ttk.Frame(self.add_window)
        form_frame.pack(padx=10, pady=10)

        ttk.Label(form_frame, text="Título:").grid(row=0, column=0, sticky="e", pady=5)
        self.titulo_entry = ttk.Entry(form_frame)
        self.titulo_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(form_frame, text="Mensagem:").grid(row=1, column=0, sticky="ne", pady=5)
        self.mensagem_text = tk.Text(form_frame, height=5, width=40)
        self.mensagem_text.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(form_frame, text="Tipo:").grid(row=2, column=0, sticky="e", pady=5)
        self.tipo_combobox = ttk.Combobox(form_frame, values=["Info", "Alerta", "Urgente"])
        self.tipo_combobox.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
        self.tipo_combobox.current(0)

        # Botões
        btn_frame = ttk.Frame(self.add_window)
        btn_frame.pack(pady=10)

        save_btn = ttk.Button(
            btn_frame,
            text="Salvar",
            bootstyle="success",
            command=self.save_notificacao
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancelar",
            bootstyle="danger",
            command=self.add_window.destroy
        )
        cancel_btn.pack(side="left", padx=5)

    def save_notificacao(self):
        """Salva nova notificação no banco de dados"""
        titulo = self.titulo_entry.get()
        mensagem = self.mensagem_text.get("1.0", "end-1c")
        tipo = self.tipo_combobox.get()

        if not titulo or not mensagem:
            messagebox.showerror("Erro", "Título e mensagem são obrigatórios!")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO notificacoes (titulo, mensagem, tipo) "
                "VALUES (?, ?, ?)",
                (titulo, mensagem, tipo)
            )
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Notificação criada com sucesso!")
            self.add_window.destroy()
            self.load_notificacoes()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar notificação: {str(e)}")

    def mark_as_read(self):
        """Marca notificação selecionada como lida"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma notificação!")
            return

        item = self.tree.item(selected)
        notificacao_id = item['values'][0]

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE notificacoes SET lida = 1 WHERE id = ?",
                (notificacao_id,)
            )
            self.conn.commit()
            self.load_notificacoes()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar como lida: {str(e)}")

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()