import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from .database import create_connection


class FuncionariosModule:
    def __init__(self, parent):
        self.parent = parent
        self.conn = create_connection()
        self.create_widgets()
        self.load_funcionarios()

    def create_widgets(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame de busca
        search_frame = ttk.LabelFrame(self.main_frame, text="Buscar Funcionário", bootstyle="info")
        search_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(search_frame, text="Nome/B.I:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)

        search_btn = ttk.Button(
            search_frame,
            text="Buscar",
            bootstyle="info-outline",
            command=self.search_funcionario
        )
        search_btn.pack(side="left", padx=5)

        # Frame de ações
        actions_frame = ttk.Frame(self.main_frame)
        actions_frame.pack(fill="x", pady=(0, 10))

        add_btn = ttk.Button(
            actions_frame,
            text="Adicionar Funcionário",
            bootstyle="success",
            command=self.open_add_funcionario
        )
        add_btn.pack(side="left", padx=5)

        edit_btn = ttk.Button(
            actions_frame,
            text="Editar",
            bootstyle="warning",
            command=self.open_edit_funcionario
        )
        edit_btn.pack(side="left", padx=5)

        remove_btn = ttk.Button(
            actions_frame,
            text="Remover",
            bootstyle="danger",
            command=self.remove_funcionario
        )
        remove_btn.pack(side="left", padx=5)

        # Tabela de funcionários
        columns = ("id", "nome", "bi", "telefone", "email", "cargo", "salario", "data_contratacao")
        self.tree = ttk.Treeview(
            self.main_frame,
            columns=columns,
            show="headings",
            bootstyle="dark"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("bi", text="B.I")
        self.tree.heading("telefone", text="Telefone")
        self.tree.heading("email", text="E-mail")
        self.tree.heading("cargo", text="Cargo")
        self.tree.heading("salario", text="Salário")
        self.tree.heading("data_contratacao", text="Data Contratação")

        self.tree.column("id", width=50)
        self.tree.column("nome", width=150)
        self.tree.column("bi", width=120)
        self.tree.column("telefone", width=120)
        self.tree.column("email", width=180)
        self.tree.column("cargo", width=120)
        self.tree.column("salario", width=100)
        self.tree.column("data_contratacao", width=120)

        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_funcionarios(self):
        """Carrega todos os funcionários na tabela"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, nome, bi, telefone, email, cargo, salario, data_contratacao 
            FROM funcionarios
        """)
        rows = cursor.fetchall()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            salario = f"R$ {row[6]:.2f}" if row[6] else ""
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], row[5], salario, row[7]))

    def search_funcionario(self):
        """Busca funcionários por nome ou BI"""
        search_term = self.search_entry.get()
        cursor = self.conn.cursor()

        if search_term:
            cursor.execute(
                "SELECT id, nome, bi, telefone, email, cargo, salario, data_contratacao "
                "FROM funcionarios WHERE nome LIKE ? OR bi LIKE ?",
                (f"%{search_term}%", f"%{search_term}%")
            )
        else:
            cursor.execute("""
                SELECT id, nome, bi, telefone, email, cargo, salario, data_contratacao 
                FROM funcionarios
            """)

        rows = cursor.fetchall()
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            salario = f"R$ {row[6]:.2f}" if row[6] else ""
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], row[5], salario, row[7]))

    def open_add_funcionario(self):
        """Abre janela para adicionar novo funcionário"""
        self.add_window = ttk.Toplevel(self.parent)
        self.add_window.title("Adicionar Funcionário")

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

        ttk.Label(form_frame, text="Cargo:").grid(row=4, column=0, sticky="e", pady=5)
        self.cargo_combobox = ttk.Combobox(
            form_frame,
            values=["Gerente", "Vendedor", "Atendente", "Técnico", "Entregador"]
        )
        self.cargo_combobox.grid(row=4, column=1, pady=5, padx=5)
        self.cargo_combobox.current(1)

        ttk.Label(form_frame, text="Salário:").grid(row=5, column=0, sticky="e", pady=5)
        self.salario_entry = ttk.Entry(form_frame)
        self.salario_entry.grid(row=5, column=1, pady=5, padx=5)

        # Botões
        btn_frame = ttk.Frame(self.add_window)
        btn_frame.pack(pady=10)

        save_btn = ttk.Button(
            btn_frame,
            text="Salvar",
            bootstyle="success",
            command=self.save_funcionario
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancelar",
            bootstyle="danger",
            command=self.add_window.destroy
        )
        cancel_btn.pack(side="left", padx=5)

    def save_funcionario(self):
        """Salva novo funcionário no banco de dados"""
        nome = self.nome_entry.get()
        cpf = self.cpf_entry.get()
        telefone = self.telefone_entry.get()
        email = self.email_entry.get()
        cargo = self.cargo_combobox.get()
        salario = self.salario_entry.get()

        if not nome or not cpf:
            messagebox.showerror("Erro", "Nome e B.I são obrigatórios!")
            return

        try:
            salario = float(salario) if salario else 0.0
        except ValueError:
            messagebox.showerror("Erro", "Salário deve ser um valor numérico!")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO funcionarios (nome, bi, telefone, email, cargo, salario) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (nome, cpf, telefone, email, cargo, salario)
            )
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Funcionário cadastrado com sucesso!")
            self.add_window.destroy()
            self.load_funcionarios()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar funcionário: {str(e)}")

    def open_edit_funcionario(self):
        """Abre janela para editar funcionário selecionado"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um funcionário para editar!")
            return

        item = self.tree.item(selected)
        funcionario_id = item['values'][0]

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM funcionarios WHERE id = ?", (funcionario_id,))
        funcionario = cursor.fetchone()

        self.edit_window = ttk.Toplevel(self.parent)
        self.edit_window.title("Editar Funcionário")
        self.current_funcionario_id = funcionario_id

        # Formulário
        form_frame = ttk.Frame(self.edit_window)
        form_frame.pack(padx=10, pady=10)

        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky="e", pady=5)
        self.edit_nome_entry = ttk.Entry(form_frame)
        self.edit_nome_entry.grid(row=0, column=1, pady=5, padx=5)
        self.edit_nome_entry.insert(0, funcionario[1])

        ttk.Label(form_frame, text="B.I:").grid(row=1, column=0, sticky="e", pady=5)
        self.edit_cpf_entry = ttk.Entry(form_frame)
        self.edit_cpf_entry.grid(row=1, column=1, pady=5, padx=5)
        self.edit_cpf_entry.insert(0, funcionario[2])

        ttk.Label(form_frame, text="Telefone:").grid(row=2, column=0, sticky="e", pady=5)
        self.edit_telefone_entry = ttk.Entry(form_frame)
        self.edit_telefone_entry.grid(row=2, column=1, pady=5, padx=5)
        self.edit_telefone_entry.insert(0, funcionario[3])

        ttk.Label(form_frame, text="E-mail:").grid(row=3, column=0, sticky="e", pady=5)
        self.edit_email_entry = ttk.Entry(form_frame)
        self.edit_email_entry.grid(row=3, column=1, pady=5, padx=5)
        self.edit_email_entry.insert(0, funcionario[4])

        ttk.Label(form_frame, text="Cargo:").grid(row=4, column=0, sticky="e", pady=5)
        self.edit_cargo_combobox = ttk.Combobox(
            form_frame,
            values=["Gerente", "Vendedor", "Atendente", "Técnico", "Entregador"]
        )
        self.edit_cargo_combobox.grid(row=4, column=1, pady=5, padx=5)
        self.edit_cargo_combobox.set(funcionario[5])

        ttk.Label(form_frame, text="Salário:").grid(row=5, column=0, sticky="e", pady=5)
        self.edit_salario_entry = ttk.Entry(form_frame)
        self.edit_salario_entry.grid(row=5, column=1, pady=5, padx=5)
        self.edit_salario_entry.insert(0, funcionario[6])

        # Botões
        btn_frame = ttk.Frame(self.edit_window)
        btn_frame.pack(pady=10)

        save_btn = ttk.Button(
            btn_frame,
            text="Salvar Alterações",
            bootstyle="success",
            command=self.update_funcionario
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancelar",
            bootstyle="danger",
            command=self.edit_window.destroy
        )
        cancel_btn.pack(side="left", padx=5)

    def update_funcionario(self):
        """Atualiza funcionário no banco de dados"""
        nome = self.edit_nome_entry.get()
        cpf = self.edit_cpf_entry.get()
        telefone = self.edit_telefone_entry.get()
        email = self.edit_email_entry.get()
        cargo = self.edit_cargo_combobox.get()
        salario = self.edit_salario_entry.get()

        if not nome or not cpf:
            messagebox.showerror("Erro", "Nome e B.I são obrigatórios!")
            return

        try:
            salario = float(salario) if salario else 0.0
        except ValueError:
            messagebox.showerror("Erro", "Salário deve ser um valor numérico!")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE funcionarios SET nome = ?, bi = ?, telefone = ?, email = ?, cargo = ?, salario = ? "
                "WHERE id = ?",
                (nome, cpf, telefone, email, cargo, salario, self.current_funcionario_id)
            )
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Funcionário atualizado com sucesso!")
            self.edit_window.destroy()
            self.load_funcionarios()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar funcionário: {str(e)}")

    def remove_funcionario(self):
        """Remove funcionário selecionado"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um funcionário para remover!")
            return

        item = self.tree.item(selected)
        funcionario_id = item['values'][0]
        funcionario_nome = item['values'][1]

        # Verificar se o funcionário está associado a algum aluguel
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM alugueis WHERE funcionario_id = ?", (funcionario_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            messagebox.showerror("Erro", "Este funcionário está associado a aluguéis e não pode ser removido!")
            return

        confirm = messagebox.askyesno(
            "Confirmar",
            f"Tem certeza que deseja remover o funcionário {funcionario_nome}?"
        )

        if confirm:
            try:
                cursor.execute("DELETE FROM funcionarios WHERE id = ?", (funcionario_id,))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Funcionário removido com sucesso!")
                self.load_funcionarios()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover funcionário: {str(e)}")

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()