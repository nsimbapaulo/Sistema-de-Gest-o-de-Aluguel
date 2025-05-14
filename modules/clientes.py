import ttkbootstrap as ttk
from tkinter import messagebox
from modules.models.database import create_connection
from modules.models.model import view_table


class ClientesModule:
    def __init__(self, parent):
        self.parent = parent
        self.conn = create_connection()
        self.create_widgets()
        self.load_clientes()

    def create_widgets(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame de busca
        search_frame = ttk.LabelFrame(self.main_frame, text="Buscar Cliente", bootstyle="info")
        search_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(search_frame, text="Nome/B.I:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)

        search_btn = ttk.Button(
            search_frame,
            text="Buscar",
            bootstyle="info-outline",
            command=self.search_cliente
        )
        search_btn.pack(side="left", padx=5)

        # Frame de ações
        actions_frame = ttk.Frame(self.main_frame)
        actions_frame.pack(fill="x", pady=(0, 10))

        add_btn = ttk.Button(
            actions_frame,
            text="Adicionar Cliente",
            bootstyle="success",
            command=self.open_add_cliente
        )
        add_btn.pack(side="left", padx=5)

        edit_btn = ttk.Button(
            actions_frame,
            text="Editar",
            bootstyle="warning",
            command=self.open_edit_cliente
        )
        edit_btn.pack(side="left", padx=5)

        remove_btn = ttk.Button(
            actions_frame,
            text="Remover",
            bootstyle="danger",
            command=self.remove_cliente
        )
        remove_btn.pack(side="left", padx=5)

        # Tabela de clientes
        columns = ("id", "nome", "B.I", "telefone", "email", "data_cadastro")
        self.tree = ttk.Treeview(
            self.main_frame,
            columns=columns,
            show="headings",
            bootstyle="dark"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("B.I", text="B.I")
        self.tree.heading("telefone", text="Telefone")
        self.tree.heading("email", text="E-mail")
        self.tree.heading("data_cadastro", text="Data Cadastro")

        self.tree.column("id", width=50)
        self.tree.column("nome", width=200)
        self.tree.column("B.I", width=120)
        self.tree.column("telefone", width=120)
        self.tree.column("email", width=200)
        self.tree.column("data_cadastro", width=120)

        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_clientes(self):
        """Carrega todos os clientes na tabela"""
        # cursor = self.conn.cursor()
        # cursor.execute("SELECT id, nome, bi, telefone, email, data_cadastro FROM clientes")
        rows = view_table("clientes", "id, nome, bi, telefone, email, data_cadastro")

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=row)

    def search_cliente(self):
        """Busca clientes por nome ou B.I"""
        search_term = self.search_entry.get()
        cursor = self.conn.cursor()

        if search_term:
            cursor.execute(
                "SELECT id, nome, bi, telefone, email, data_cadastro FROM clientes "
                "WHERE nome LIKE ? OR bi LIKE ?",
                (f"%{search_term}%", f"%{search_term}%")
            )
        else:
            cursor.execute("SELECT id, nome, bi, telefone, email, data_cadastro FROM clientes")

        rows = cursor.fetchall()
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=row)

    def open_add_cliente(self):
        """Abre janela para adicionar novo cliente"""
        self.add_window = ttk.Toplevel(self.parent)
        self.add_window.title("Adicionar Cliente")

        # Formulário
        form_frame = ttk.Frame(self.add_window)
        form_frame.pack(padx=10, pady=10)

        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky="e", pady=5)
        self.nome_entry = ttk.Entry(form_frame)
        self.nome_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="B.I:").grid(row=1, column=0, sticky="e", pady=5)
        self.cpf_entry = ttk.Entry(form_frame)
        self.cpf_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Telefone:").grid(row=2, column=0, sticky="e", pady=5)
        self.telefone_entry = ttk.Entry(form_frame)
        self.telefone_entry.grid(row=2, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="E-mail:").grid(row=3, column=0, sticky="e", pady=5)
        self.email_entry = ttk.Entry(form_frame)
        self.email_entry.grid(row=3, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Endereço:").grid(row=4, column=0, sticky="e", pady=5)
        self.endereco_entry = ttk.Entry(form_frame)
        self.endereco_entry.grid(row=4, column=1, pady=5, padx=5)

        # Botões
        btn_frame = ttk.Frame(self.add_window)
        btn_frame.pack(pady=10)

        save_btn = ttk.Button(
            btn_frame,
            text="Salvar",
            bootstyle="success",
            command=self.save_cliente
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancelar",
            bootstyle="danger",
            command=self.add_window.destroy
        )
        cancel_btn.pack(side="left", padx=5)

    def save_cliente(self):
        """Salva novo cliente no banco de dados"""
        nome = self.nome_entry.get()
        cpf = self.cpf_entry.get()
        telefone = self.telefone_entry.get()
        email = self.email_entry.get()
        endereco = self.endereco_entry.get()

        if not nome:
            messagebox.showerror("Erro", "O nome é obrigatório!")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO clientes (nome, bi, telefone, email, endereco) "
                "VALUES (?, ?, ?, ?, ?)",
                (nome, cpf, telefone, email, endereco)
            )
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
            self.add_window.destroy()
            self.load_clientes()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar cliente: {str(e)}")

    def open_edit_cliente(self):
        """Abre janela para editar cliente selecionado"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar!")
            return

        item = self.tree.item(selected)
        cliente_id = item['values'][0]

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        cliente = cursor.fetchone()

        self.edit_window = ttk.Toplevel(self.parent)
        self.edit_window.title("Editar Cliente")
        self.current_cliente_id = cliente_id

        # Formulário
        form_frame = ttk.Frame(self.edit_window)
        form_frame.pack(padx=10, pady=10)

        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky="e", pady=5)
        self.edit_nome_entry = ttk.Entry(form_frame)
        self.edit_nome_entry.grid(row=0, column=1, pady=5, padx=5)
        self.edit_nome_entry.insert(0, cliente[1])

        ttk.Label(form_frame, text="B.I:").grid(row=1, column=0, sticky="e", pady=5)
        self.edit_cpf_entry = ttk.Entry(form_frame)
        self.edit_cpf_entry.grid(row=1, column=1, pady=5, padx=5)
        self.edit_cpf_entry.insert(0, cliente[2])

        ttk.Label(form_frame, text="Telefone:").grid(row=2, column=0, sticky="e", pady=5)
        self.edit_telefone_entry = ttk.Entry(form_frame)
        self.edit_telefone_entry.grid(row=2, column=1, pady=5, padx=5)
        self.edit_telefone_entry.insert(0, cliente[3])

        ttk.Label(form_frame, text="E-mail:").grid(row=3, column=0, sticky="e", pady=5)
        self.edit_email_entry = ttk.Entry(form_frame)
        self.edit_email_entry.grid(row=3, column=1, pady=5, padx=5)
        self.edit_email_entry.insert(0, cliente[4])

        ttk.Label(form_frame, text="Endereço:").grid(row=4, column=0, sticky="e", pady=5)
        self.edit_endereco_entry = ttk.Entry(form_frame)
        self.edit_endereco_entry.grid(row=4, column=1, pady=5, padx=5)
        self.edit_endereco_entry.insert(0, cliente[5])

        # Botões
        btn_frame = ttk.Frame(self.edit_window)
        btn_frame.pack(pady=10)

        save_btn = ttk.Button(
            btn_frame,
            text="Salvar Alterações",
            bootstyle="success",
            command=self.update_cliente
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancelar",
            bootstyle="danger",
            command=self.edit_window.destroy
        )
        cancel_btn.pack(side="left", padx=5)

    def update_cliente(self):
        """Atualiza cliente no banco de dados"""
        nome = self.edit_nome_entry.get()
        cpf = self.edit_cpf_entry.get()
        telefone = self.edit_telefone_entry.get()
        email = self.edit_email_entry.get()
        endereco = self.edit_endereco_entry.get()

        if not nome:
            messagebox.showerror("Erro", "O nome é obrigatório!")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE clientes SET nome = ?, bi = ?, telefone = ?, email = ?, endereco = ? "
                "WHERE id = ?",
                (nome, cpf, telefone, email, endereco, self.current_cliente_id)
            )
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")
            self.edit_window.destroy()
            self.load_clientes()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar cliente: {str(e)}")

    def remove_cliente(self):
        """Remove cliente selecionado"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um cliente para remover!")
            return

        item = self.tree.item(selected)
        cliente_id = item['values'][0]
        cliente_nome = item['values'][1]

        confirm = messagebox.askyesno(
            "Confirmar",
            f"Tem certeza que deseja remover o cliente {cliente_nome}?"
        )

        if confirm:
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Cliente removido com sucesso!")
                self.load_clientes()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover cliente: {str(e)}")

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()