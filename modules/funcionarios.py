import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from modules.models.database import create_connection
import hashlib
from datetime import datetime


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

        ttk.Label(search_frame, text="Nome/BI/Usuário:").pack(side="left", padx=5)
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

        reset_pass_btn = ttk.Button(
            actions_frame,
            text="Redefinir Senha",
            bootstyle="info",
            command=self.open_reset_password
        )
        reset_pass_btn.pack(side="left", padx=5)

        toggle_status_btn = ttk.Button(
            actions_frame,
            text="Ativar/Desativar",
            bootstyle="secondary",
            command=self.toggle_funcionario_status
        )
        toggle_status_btn.pack(side="left", padx=5)

        remove_btn = ttk.Button(
            actions_frame,
            text="Remover",
            bootstyle="danger",
            command=self.remove_funcionario
        )
        remove_btn.pack(side="left", padx=5)

        # Tabela de funcionários
        columns = ("id", "nome", "usuario", "bi", "cargo", "is_admin", "status")
        self.tree = ttk.Treeview(
            self.main_frame,
            columns=columns,
            show="headings",
            bootstyle="dark",
            selectmode="browse"
        )

        # Configurar cabeçalhos
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("usuario", text="Usuário")
        self.tree.heading("bi", text="BI")
        self.tree.heading("cargo", text="Cargo")
        self.tree.heading("is_admin", text="Nível Acesso")
        self.tree.heading("status", text="Status")

        # Configurar largura das colunas
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nome", width=150)
        self.tree.column("usuario", width=100)
        self.tree.column("bi", width=120, anchor="center")
        self.tree.column("cargo", width=120)
        self.tree.column("is_admin", width=100, anchor="center")
        self.tree.column("status", width=80, anchor="center")

        # Barra de rolagem
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Tags para estilo
        self.tree.tag_configure('admin', background='#e6f3ff')
        self.tree.tag_configure('inactive', background='#ffe6e6')

    def load_funcionarios(self):
        """Carrega todos os funcionários na tabela"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, nome, usuario, bi, cargo, is_admin, 
                   CASE WHEN ativo = 1 THEN 'Ativo' ELSE 'Inativo' END as status
            FROM funcionarios
            ORDER BY nome
        """)
        rows = cursor.fetchall()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            nivel_acesso = "Admin" if row[5] else "Funcionário"
            tags = ('admin',) if row[5] else ()
            tags = ('inactive',) if row[6] == 'Inativo' else tags
            self.tree.insert("", "end", values=(
                row[0], row[1], row[2], row[3], row[4], nivel_acesso, row[6]
            ), tags=tags)

    def search_funcionario(self):
        """Busca funcionários por nome, BI ou usuário"""
        search_term = self.search_entry.get()
        cursor = self.conn.cursor()

        if search_term:
            cursor.execute("""
                SELECT id, nome, usuario, bi, cargo, is_admin,
                       CASE WHEN ativo = 1 THEN 'Ativo' ELSE 'Inativo' END as status
                FROM funcionarios
                WHERE nome LIKE ? OR bi LIKE ? OR usuario LIKE ?
                ORDER BY nome
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        else:
            cursor.execute("""
                SELECT id, nome, usuario, bi, cargo, is_admin,
                       CASE WHEN ativo = 1 THEN 'Ativo' ELSE 'Inativo' END as status
                FROM funcionarios
                ORDER BY nome
            """)

        rows = cursor.fetchall()
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            nivel_acesso = "Admin" if row[5] else "Funcionário"
            tags = ('admin',) if row[5] else ()
            tags = ('inactive',) if row[6] == 'Inativo' else tags
            self.tree.insert("", "end", values=(
                row[0], row[1], row[2], row[3], row[4], nivel_acesso, row[6]
            ), tags=tags)

    def open_add_funcionario(self):
        """Abre janela para adicionar novo funcionário"""
        self.add_window = ttk.Toplevel(self.parent)
        self.add_window.title("Adicionar Funcionário")
        self.add_window.geometry("500x550")

        # Frame principal
        main_frame = ttk.Frame(self.add_window)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)

        # Aba Informações Pessoais
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="Informações Pessoais")

        # Formulário
        ttk.Label(info_frame, text="Nome Completo:").grid(row=0, column=0, sticky="e", pady=5)
        self.nome_entry = ttk.Entry(info_frame)
        self.nome_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(info_frame, text="BI:").grid(row=1, column=0, sticky="e", pady=5)
        self.cpf_entry = ttk.Entry(info_frame)
        self.cpf_entry.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(info_frame, text="Telefone:").grid(row=2, column=0, sticky="e", pady=5)
        self.telefone_entry = ttk.Entry(info_frame)
        self.telefone_entry.grid(row=2, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(info_frame, text="E-mail:").grid(row=3, column=0, sticky="e", pady=5)
        self.email_entry = ttk.Entry(info_frame)
        self.email_entry.grid(row=3, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(info_frame, text="Endereço:").grid(row=4, column=0, sticky="ne", pady=5)
        self.endereco_text = tk.Text(info_frame, height=3, width=30)
        self.endereco_text.grid(row=4, column=1, pady=5, padx=5, sticky="ew")

        # Aba Dados Profissionais
        prof_frame = ttk.Frame(notebook)
        notebook.add(prof_frame, text="Dados Profissionais")

        ttk.Label(prof_frame, text="Cargo:").grid(row=0, column=0, sticky="e", pady=5)
        self.cargo_combobox = ttk.Combobox(
            prof_frame,
            values=["Gerente", "Vendedor", "Atendente", "Técnico", "Entregador", "Administrativo"]
        )
        self.cargo_combobox.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        self.cargo_combobox.current(0)

        ttk.Label(prof_frame, text="Salário:").grid(row=1, column=0, sticky="e", pady=5)
        self.salario_entry = ttk.Entry(prof_frame)
        self.salario_entry.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(prof_frame, text="Data Contratação:").grid(row=2, column=0, sticky="e", pady=5)
        self.data_contratacao_entry = ttk.DateEntry(prof_frame)
        self.data_contratacao_entry.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
        self.data_contratacao_entry.entry.delete(0, "end")
        self.data_contratacao_entry.entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

        # Aba Acesso ao Sistema
        access_frame = ttk.Frame(notebook)
        notebook.add(access_frame, text="Acesso ao Sistema")

        ttk.Label(access_frame, text="Nome de Usuário:").grid(row=0, column=0, sticky="e", pady=5)
        self.usuario_entry = ttk.Entry(access_frame)
        self.usuario_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(access_frame, text="Senha:").grid(row=1, column=0, sticky="e", pady=5)
        self.senha_entry = ttk.Entry(access_frame, show="*")
        self.senha_entry.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(access_frame, text="Confirmar Senha:").grid(row=2, column=0, sticky="e", pady=5)
        self.confirmar_senha_entry = ttk.Entry(access_frame, show="*")
        self.confirmar_senha_entry.grid(row=2, column=1, pady=5, padx=5, sticky="ew")

        self.is_admin_var = tk.BooleanVar()
        admin_check = ttk.Checkbutton(
            access_frame,
            text="Acesso de Administrador",
            variable=self.is_admin_var,
            bootstyle="info-round-toggle"
        )
        admin_check.grid(row=3, column=1, pady=10, padx=5, sticky="w")

        self.ativo_var = tk.BooleanVar(value=True)
        ativo_check = ttk.Checkbutton(
            access_frame,
            text="Usuário Ativo",
            variable=self.ativo_var,
            bootstyle="success-round-toggle"
        )
        ativo_check.grid(row=4, column=1, pady=5, padx=5, sticky="w")

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)

        save_btn = ttk.Button(
            btn_frame,
            text="Salvar Funcionário",
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
        # Obter valores do formulário
        nome = self.nome_entry.get()
        cpf = self.cpf_entry.get()
        telefone = self.telefone_entry.get()
        email = self.email_entry.get()
        endereco = self.endereco_text.get("1.0", "end-1c")
        cargo = self.cargo_combobox.get()
        salario = self.salario_entry.get()
        data_contratacao = self.data_contratacao_entry.entry.get()
        usuario = self.usuario_entry.get()
        senha = self.senha_entry.get()
        confirmar_senha = self.confirmar_senha_entry.get()
        is_admin = self.is_admin_var.get()
        ativo = self.ativo_var.get()

        # Validações
        if not nome or not cpf or not usuario:
            messagebox.showerror("Erro", "Nome, BI e Usuário são obrigatórios!")
            return

        if not senha or len(senha) < 6:
            messagebox.showerror("Erro", "A senha deve ter pelo menos 6 caracteres!")
            return

        if senha != confirmar_senha:
            messagebox.showerror("Erro", "As senhas não coincidem!")
            return

        try:
            salario = float(salario) if salario else 0.0
        except ValueError:
            messagebox.showerror("Erro", "Salário deve ser um valor numérico válido!")
            return

        try:
            # Converter data para formato SQL
            data_contratacao = datetime.strptime(data_contratacao, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Data de contratação inválida! Use DD/MM/AAAA")
            return

        # Hash da senha
        hashed_password = hashlib.sha256(senha.encode()).hexdigest()

        try:
            cursor = self.conn.cursor()

            # Verificar se usuário ou BI já existem
            cursor.execute("SELECT id FROM funcionarios WHERE usuario = ? OR bi = ?", (usuario, cpf))
            if cursor.fetchone():
                messagebox.showerror("Erro", "Usuário ou BI já cadastrados!")
                return

            # Inserir novo funcionário
            cursor.execute("""
                INSERT INTO funcionarios (
                    nome, bi, telefone, email, endereco, cargo, salario, 
                    data_contratacao, usuario, senha, is_admin, ativo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nome, cpf, telefone, email, endereco, cargo, salario,
                data_contratacao, usuario, hashed_password, int(is_admin), int(ativo)
            ))

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

        if not funcionario:
            messagebox.showerror("Erro", "Funcionário não encontrado!")
            return

        self.edit_window = ttk.Toplevel(self.parent)
        self.edit_window.title(f"Editar Funcionário - {funcionario[1]}")
        self.edit_window.geometry("500x550")
        self.current_funcionario_id = funcionario_id

        # Frame principal
        main_frame = ttk.Frame(self.edit_window)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)

        # Aba Informações Pessoais
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="Informações Pessoais")

        # Formulário
        ttk.Label(info_frame, text="Nome Completo:").grid(row=0, column=0, sticky="e", pady=5)
        self.edit_nome_entry = ttk.Entry(info_frame)
        self.edit_nome_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        self.edit_nome_entry.insert(0, funcionario[1])

        ttk.Label(info_frame, text="BI:").grid(row=1, column=0, sticky="e", pady=5)
        self.edit_cpf_entry = ttk.Entry(info_frame)
        self.edit_cpf_entry.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
        self.edit_cpf_entry.insert(0, funcionario[2])

        ttk.Label(info_frame, text="Telefone:").grid(row=2, column=0, sticky="e", pady=5)
        self.edit_telefone_entry = ttk.Entry(info_frame)
        self.edit_telefone_entry.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
        self.edit_telefone_entry.insert(0, funcionario[3])

        ttk.Label(info_frame, text="E-mail:").grid(row=3, column=0, sticky="e", pady=5)
        self.edit_email_entry = ttk.Entry(info_frame)
        self.edit_email_entry.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
        self.edit_email_entry.insert(0, funcionario[4])

        ttk.Label(info_frame, text="Endereço:").grid(row=4, column=0, sticky="ne", pady=5)
        self.edit_endereco_text = tk.Text(info_frame, height=3, width=30)
        self.edit_endereco_text.grid(row=4, column=1, pady=5, padx=5, sticky="ew")
        self.edit_endereco_text.insert("1.0", funcionario[5])

        # Aba Dados Profissionais
        prof_frame = ttk.Frame(notebook)
        notebook.add(prof_frame, text="Dados Profissionais")

        ttk.Label(prof_frame, text="Cargo:").grid(row=0, column=0, sticky="e", pady=5)
        self.edit_cargo_combobox = ttk.Combobox(
            prof_frame,
            values=["Gerente", "Vendedor", "Atendente", "Técnico", "Entregador", "Administrativo"]
        )
        self.edit_cargo_combobox.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        self.edit_cargo_combobox.set(funcionario[6])

        ttk.Label(prof_frame, text="Salário:").grid(row=1, column=0, sticky="e", pady=5)
        self.edit_salario_entry = ttk.Entry(prof_frame)
        self.edit_salario_entry.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
        self.edit_salario_entry.insert(0, funcionario[7])

        ttk.Label(prof_frame, text="Data Contratação:").grid(row=2, column=0, sticky="e", pady=5)
        self.edit_data_contratacao_entry = ttk.DateEntry(prof_frame)
        self.edit_data_contratacao_entry.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
        self.edit_data_contratacao_entry.entry.delete(0, "end")
        self.edit_data_contratacao_entry.entry.insert(0, funcionario[8])

        # Aba Acesso ao Sistema
        access_frame = ttk.Frame(notebook)
        notebook.add(access_frame, text="Acesso ao Sistema")

        ttk.Label(access_frame, text="Nome de Usuário:").grid(row=0, column=0, sticky="e", pady=5)
        self.edit_usuario_entry = ttk.Entry(access_frame)
        self.edit_usuario_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        self.edit_usuario_entry.insert(0, funcionario[9])

        self.edit_is_admin_var = tk.BooleanVar(value=bool(funcionario[11]))
        admin_check = ttk.Checkbutton(
            access_frame,
            text="Acesso de Administrador",
            variable=self.edit_is_admin_var,
            bootstyle="info-round-toggle"
        )
        admin_check.grid(row=1, column=1, pady=10, padx=5, sticky="w")

        self.edit_ativo_var = tk.BooleanVar(value=bool(funcionario[12]))
        ativo_check = ttk.Checkbutton(
            access_frame,
            text="Usuário Ativo",
            variable=self.edit_ativo_var,
            bootstyle="success-round-toggle"
        )
        ativo_check.grid(row=2, column=1, pady=5, padx=5, sticky="w")

        # Botões
        btn_frame = ttk.Frame(main_frame)
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
        """Atualiza os dados do funcionário"""
        # Obter valores do formulário
        nome = self.edit_nome_entry.get()
        cpf = self.edit_cpf_entry.get()
        telefone = self.edit_telefone_entry.get()
        email = self.edit_email_entry.get()
        endereco = self.edit_endereco_text.get("1.0", "end-1c")
        cargo = self.edit_cargo_combobox.get()
        salario = self.edit_salario_entry.get()
        data_contratacao = self.edit_data_contratacao_entry.entry.get()
        usuario = self.edit_usuario_entry.get()
        is_admin = self.edit_is_admin_var.get()
        ativo = self.edit_ativo_var.get()

        # Validações
        if not nome or not cpf or not usuario:
            messagebox.showerror("Erro", "Nome, BI e Usuário são obrigatórios!")
            return

        try:
            salario = float(salario) if salario else 0.0
        except ValueError:
            messagebox.showerror("Erro", "Salário deve ser um valor numérico válido!")
            return

        try:
            # Converter data para formato SQL
            data_contratacao = datetime.strptime(data_contratacao, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Data de contratação inválida! Use DD/MM/AAAA")
            return

        try:
            cursor = self.conn.cursor()

            # Verificar se usuário ou BI já existem (excluindo o próprio funcionário)
            cursor.execute("""
                SELECT id FROM funcionarios 
                WHERE (usuario = ? OR bi = ?) AND id != ?
            """, (usuario, cpf, self.current_funcionario_id))

            if cursor.fetchone():
                messagebox.showerror("Erro", "Usuário ou BI já cadastrados para outro funcionário!")
                return

            # Atualizar funcionário
            cursor.execute("""
                UPDATE funcionarios SET
                    nome = ?, bi = ?, telefone = ?, email = ?, endereco = ?,
                    cargo = ?, salario = ?, data_contratacao = ?, usuario = ?,
                    is_admin = ?, ativo = ?
                WHERE id = ?
            """, (
                nome, cpf, telefone, email, endereco, cargo, salario,
                data_contratacao, usuario, int(is_admin), int(ativo),
                self.current_funcionario_id
            ))

            self.conn.commit()
            messagebox.showinfo("Sucesso", "Dados do funcionário atualizados com sucesso!")
            self.edit_window.destroy()
            self.load_funcionarios()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar funcionário: {str(e)}")

    def open_reset_password(self):
        """Abre janela para redefinir senha do funcionário"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um funcionário!")
            return

        item = self.tree.item(selected)
        funcionario_id = item['values'][0]
        funcionario_nome = item['values'][1]

        self.reset_window = ttk.Toplevel(self.parent)
        self.reset_window.title(f"Redefinir Senha - {funcionario_nome}")
        self.reset_window.geometry("400x250")

        # Frame principal
        main_frame = ttk.Frame(self.reset_window)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        ttk.Label(main_frame, text="Nova Senha:").grid(row=0, column=0, sticky="e", pady=10)
        self.new_pass_entry = ttk.Entry(main_frame, show="*")
        self.new_pass_entry.grid(row=0, column=1, pady=10, padx=5, sticky="ew")

        ttk.Label(main_frame, text="Confirmar Senha:").grid(row=1, column=0, sticky="e", pady=10)
        self.confirm_pass_entry = ttk.Entry(main_frame, show="*")
        self.confirm_pass_entry.grid(row=1, column=1, pady=10, padx=5, sticky="ew")

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)

        save_btn = ttk.Button(
            btn_frame,
            text="Salvar Nova Senha",
            bootstyle="success",
            command=lambda: self.reset_password(funcionario_id)
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancelar",
            bootstyle="danger",
            command=self.reset_window.destroy
        )
        cancel_btn.pack(side="left", padx=5)

    def reset_password(self, funcionario_id):
        """Redefine a senha do funcionário"""
        new_pass = self.new_pass_entry.get()
        confirm_pass = self.confirm_pass_entry.get()

        if not new_pass or len(new_pass) < 6:
            messagebox.showerror("Erro", "A senha deve ter pelo menos 6 caracteres!")
            return

        if new_pass != confirm_pass:
            messagebox.showerror("Erro", "As senhas não coincidem!")
            return

        try:
            hashed_password = hashlib.sha256(new_pass.encode()).hexdigest()

            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE funcionarios SET senha = ? WHERE id = ?",
                (hashed_password, funcionario_id)
            )
            self.conn.commit()

            messagebox.showinfo("Sucesso", "Senha redefinida com sucesso!")
            self.reset_window.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao redefinir senha: {str(e)}")

    def toggle_funcionario_status(self):
        """Ativa/desativa um funcionário"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um funcionário!")
            return

        item = self.tree.item(selected)
        funcionario_id = item['values'][0]
        funcionario_nome = item['values'][1]
        status_atual = item['values'][6]

        novo_status = 0 if status_atual == "Ativo" else 1
        acao = "desativar" if status_atual == "Ativo" else "ativar"

        confirm = messagebox.askyesno(
            "Confirmar",
            f"Tem certeza que deseja {acao} o funcionário {funcionario_nome}?"
        )

        if confirm:
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    "UPDATE funcionarios SET ativo = ? WHERE id = ?",
                    (novo_status, funcionario_id)
                )
                self.conn.commit()

                messagebox.showinfo("Sucesso", f"Funcionário {acao}do com sucesso!")
                self.load_funcionarios()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao {acao} funcionário: {str(e)}")

    def remove_funcionario(self):
        """Remove um funcionário do sistema"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um funcionário!")
            return

        item = self.tree.item(selected)
        funcionario_id = item['values'][0]
        funcionario_nome = item['values'][1]

        # Verificar se o funcionário está associado a algum aluguel
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM alugueis WHERE funcionario_id = ?", (funcionario_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            messagebox.showerror("Erro",
                                 "Este funcionário está associado a aluguéis e não pode ser removido!\n"
                                 "Você pode desativar o acesso dele no sistema.")
            return

        confirm = messagebox.askyesno(
            "Confirmar Remoção",
            f"Tem certeza que deseja remover permanentemente o funcionário {funcionario_nome}?\n"
            "Esta ação não pode ser desfeita!"
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