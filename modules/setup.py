import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .database import create_connection
import hashlib
import os
import shutil  # para manipulação de arquivos

class FirstRunSetup:
    def __init__(self, root, on_setup_complete):
        self.root = root
        self.on_setup_complete = on_setup_complete
        self.conn = create_connection()
        self.create_widgets()

    def create_widgets(self):
        """Cria a interface do assistente de configuração inicial"""
        self.setup_window = ttk.Toplevel(self.root)
        self.setup_window.title("Configuração Inicial do Sistema")
        self.setup_window.geometry("700x550")
        self.setup_window.resizable(False, False)

        # Centralizar na tela
        window_width = 700
        window_height = 550
        position_right = int(self.setup_window.winfo_screenwidth() / 2 - window_width / 2)
        position_down = int(self.setup_window.winfo_screenheight() / 2 - window_height / 2)
        self.setup_window.geometry(f"+{position_right}+{position_down}")

        # Frame principal
        main_frame = ttk.Frame(self.setup_window)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Título
        ttk.Label(
            main_frame,
            text="Configuração Inicial",
            font=('Helvetica', 16, 'bold')
        ).pack(pady=(0, 20))

        # Notebook para as etapas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Etapa 1: Informações da Empresa
        self.create_company_info_tab()

        # Etapa 2: Administrador Principal
        self.create_admin_account_tab()

        # Etapa 3: Configurações Iniciais
        self.create_initial_settings_tab()

        # Botões de navegação
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)

        self.back_btn = ttk.Button(
            btn_frame,
            text="Voltar",
            bootstyle="secondary",
            command=self.prev_step,
            state="disabled"
        )
        self.back_btn.pack(side="left", padx=5)

        self.next_btn = ttk.Button(
            btn_frame,
            text="Próximo",
            bootstyle="primary",
            command=self.next_step
        )
        self.next_btn.pack(side="left", padx=5)

        self.current_step = 0
        self.update_navigation()

    def create_company_info_tab(self):
        """Cria a aba de informações da empresa"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="1. Informações da Empresa")

        # Logo da empresa
        logo_frame = ttk.Frame(tab)
        logo_frame.pack(pady=(0, 20))

        ttk.Label(logo_frame, text="Logo da Empresa:").pack(anchor="w")
        self.logo_path = tk.StringVar()

        logo_control = ttk.Frame(logo_frame)
        logo_control.pack(fill="x")

        ttk.Entry(logo_control, textvariable=self.logo_path, state="readonly").pack(side="left", fill="x", expand=True,
                                                                                    padx=(0, 5))
        ttk.Button(
            logo_control,
            text="Selecionar",
            command=self.select_logo,
            width=10
        ).pack(side="left")

        # Informações básicas
        form_frame = ttk.Frame(tab)
        form_frame.pack(fill="x")

        ttk.Label(form_frame, text="Nome da Empresa:").grid(row=0, column=0, sticky="e", pady=5)
        self.company_name = ttk.Entry(form_frame)
        self.company_name.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(form_frame, text="CNPJ:").grid(row=1, column=0, sticky="e", pady=5)
        self.company_cnpj = ttk.Entry(form_frame)
        self.company_cnpj.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(form_frame, text="Telefone:").grid(row=2, column=0, sticky="e", pady=5)
        self.company_phone = ttk.Entry(form_frame)
        self.company_phone.grid(row=2, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(form_frame, text="E-mail:").grid(row=3, column=0, sticky="e", pady=5)
        self.company_email = ttk.Entry(form_frame)
        self.company_email.grid(row=3, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(form_frame, text="Endereço:").grid(row=4, column=0, sticky="ne", pady=5)
        self.company_address = tk.Text(form_frame, height=4, width=30)
        self.company_address.grid(row=4, column=1, pady=5, padx=5, sticky="ew")

        # Configurar peso das colunas
        form_frame.columnconfigure(1, weight=1)

    def create_admin_account_tab(self):
        """Cria a aba de conta do administrador"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="2. Administrador")

        form_frame = ttk.Frame(tab)
        form_frame.pack(fill="x", pady=10)

        ttk.Label(form_frame, text="Nome Completo:").grid(row=0, column=0, sticky="e", pady=5)
        self.admin_name = ttk.Entry(form_frame)
        self.admin_name.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(form_frame, text="CPF:").grid(row=1, column=0, sticky="e", pady=5)
        self.admin_cpf = ttk.Entry(form_frame)
        self.admin_cpf.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(form_frame, text="E-mail:").grid(row=2, column=0, sticky="e", pady=5)
        self.admin_email = ttk.Entry(form_frame)
        self.admin_email.grid(row=2, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(form_frame, text="Nome de Usuário:").grid(row=3, column=0, sticky="e", pady=5)
        self.admin_username = ttk.Entry(form_frame)
        self.admin_username.grid(row=3, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(form_frame, text="Senha:").grid(row=4, column=0, sticky="e", pady=5)
        self.admin_password = ttk.Entry(form_frame, show="*")
        self.admin_password.grid(row=4, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(form_frame, text="Confirmar Senha:").grid(row=5, column=0, sticky="e", pady=5)
        self.admin_confirm_password = ttk.Entry(form_frame, show="*")
        self.admin_confirm_password.grid(row=5, column=1, pady=5, padx=5, sticky="ew")

        form_frame.columnconfigure(1, weight=1)

    def create_initial_settings_tab(self):
        """Cria a aba de configurações iniciais"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="3. Configurações")

        # Configurações do sistema
        settings_frame = ttk.LabelFrame(tab, text="Preferências do Sistema")
        settings_frame.pack(fill="x", pady=10)

        ttk.Label(settings_frame, text="Tema da Interface:").grid(row=0, column=0, sticky="e", pady=5)
        self.theme_choice = ttk.Combobox(
            settings_frame,
            values=["superhero", "litera", "minty", "pulse", "solar"],
            state="readonly"
        )
        self.theme_choice.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        self.theme_choice.current(0)

        ttk.Label(settings_frame, text="Moeda:").grid(row=1, column=0, sticky="e", pady=5)
        self.currency = ttk.Entry(settings_frame)
        self.currency.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
        self.currency.insert(0, "R$")

        # Diretórios
        dir_frame = ttk.LabelFrame(tab, text="Diretórios")
        dir_frame.pack(fill="x", pady=10)

        ttk.Label(dir_frame, text="Pasta de Backup:").grid(row=0, column=0, sticky="e", pady=5)
        self.backup_dir = tk.StringVar()
        self.backup_dir.set(os.path.join(os.getcwd(), "backups"))

        backup_control = ttk.Frame(dir_frame)
        backup_control.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        ttk.Entry(backup_control, textvariable=self.backup_dir, state="readonly").pack(side="left", fill="x",
                                                                                       expand=True, padx=(0, 5))
        ttk.Button(
            backup_control,
            text="Selecionar",
            command=lambda: self.select_directory(self.backup_dir),
            width=10
        ).pack(side="left")

        ttk.Label(dir_frame, text="Pasta de Relatórios:").grid(row=1, column=0, sticky="e", pady=5)
        self.reports_dir = tk.StringVar()
        self.reports_dir.set(os.path.join(os.getcwd(), "relatorios"))

        reports_control = ttk.Frame(dir_frame)
        reports_control.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        ttk.Entry(reports_control, textvariable=self.reports_dir, state="readonly").pack(side="left", fill="x",
                                                                                         expand=True, padx=(0, 5))
        ttk.Button(
            reports_control,
            text="Selecionar",
            command=lambda: self.select_directory(self.reports_dir),
            width=10
        ).pack(side="left")

        dir_frame.columnconfigure(1, weight=1)

        # Resumo
        ttk.Label(
            tab,
            text="Revise todas as informações antes de finalizar a configuração.",
            font=('Helvetica', 9)
        ).pack(pady=10)

    def select_logo(self):
        """Seleciona o logo da empresa e copia para o diretório do sistema"""
        filetypes = [
            ("Imagens", "*.png *.jpg *.jpeg *.bmp"),
            ("Todos os arquivos", "*.*")
        ]

        try:
            filename = filedialog.askopenfilename(
                title="Selecione o logo da empresa",
                initialdir=os.path.expanduser("~"),  # Começa no diretório do usuário
                filetypes=filetypes
            )

            if filename:
                # Criar diretório para assets se não existir
                assets_dir = os.path.join(os.getcwd(), "assets")
                os.makedirs(assets_dir, exist_ok=True)

                # Gerar nome único para o arquivo
                ext = os.path.splitext(filename)[1]
                dest_filename = f"company_logo{ext}"
                dest_path = os.path.join(assets_dir, dest_filename)

                # Copiar arquivo (substitui se já existir)
                shutil.copy(filename, dest_path)
                self.logo_path.set(dest_path)

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar a imagem:\n{str(e)}")

    def select_directory(self, target_var):
        """Seleciona um diretório e atualiza a variável de controle"""
        try:
            dir_path = filedialog.askdirectory(
                title="Selecione o diretório",
                initialdir=os.path.expanduser("~"),  # Começa no diretório do usuário
                mustexist=True  # Só permite selecionar diretórios existentes
            )

            if dir_path:
                # Verificar permissão de escrita
                if os.access(dir_path, os.W_OK):
                    target_var.set(dir_path)
                else:
                    messagebox.showerror("Erro", "Sem permissão de escrita no diretório selecionado!")

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível selecionar o diretório:\n{str(e)}")

    def next_step(self):
        """Avança para a próxima etapa do assistente"""
        if self.current_step == 0:
            # Validar informações da empresa
            if not self.validate_company_info():
                return
        elif self.current_step == 1:
            # Validar conta do administrador
            if not self.validate_admin_account():
                return

        self.current_step += 1
        self.update_navigation()

    def prev_step(self):
        """Volta para a etapa anterior do assistente"""
        self.current_step -= 1
        self.update_navigation()

    def update_navigation(self):
        """Atualiza a navegação entre as etapas"""
        self.notebook.select(self.current_step)

        # Atualizar estado dos botões
        self.back_btn.config(state="normal" if self.current_step > 0 else "disabled")

        if self.current_step == self.notebook.index("end") - 1:
            self.next_btn.config(text="Finalizar", bootstyle="success")
            self.next_btn.config(command=self.finish_setup)
        else:
            self.next_btn.config(text="Próximo", bootstyle="primary")
            self.next_btn.config(command=self.next_step)

    def validate_company_info(self):
        """Valida as informações da empresa"""
        if not self.company_name.get():
            messagebox.showerror("Erro", "O nome da empresa é obrigatório!")
            return False

        if not self.company_cnpj.get():
            messagebox.showerror("Erro", "O CNPJ da empresa é obrigatório!")
            return False

        # Validação básica de CNPJ (apenas verifica se tem 14 dígitos)
        cnpj = ''.join(filter(str.isdigit, self.company_cnpj.get()))
        if len(cnpj) != 14:
            messagebox.showerror("Erro", "CNPJ inválido! Deve conter 14 dígitos.")
            return False

        return True

    def validate_admin_account(self):
        """Valida a conta do administrador"""
        if not self.admin_name.get():
            messagebox.showerror("Erro", "O nome do administrador é obrigatório!")
            return False

        if not self.admin_cpf.get():
            messagebox.showerror("Erro", "O CPF do administrador é obrigatório!")
            return False

        # Validação básica de CPF (apenas verifica se tem 11 dígitos)
        cpf = ''.join(filter(str.isdigit, self.admin_cpf.get()))
        if len(cpf) != 11:
            messagebox.showerror("Erro", "CPF inválido! Deve conter 11 dígitos.")
            return False

        if not self.admin_username.get():
            messagebox.showerror("Erro", "O nome de usuário é obrigatório!")
            return False

        if not self.admin_password.get():
            messagebox.showerror("Erro", "A senha é obrigatória!")
            return False

        if len(self.admin_password.get()) < 6:
            messagebox.showerror("Erro", "A senha deve ter pelo menos 6 caracteres!")
            return False

        if self.admin_password.get() != self.admin_confirm_password.get():
            messagebox.showerror("Erro", "As senhas não coincidem!")
            return False

        return True

    def finish_setup(self):
        """Finaliza a configuração inicial do sistema"""
        if not self.validate_company_info() or not self.validate_admin_account():
            return

        try:
            cursor = self.conn.cursor()

            # Criar tabela de configurações se não existir
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT,
                    company_cnpj TEXT,
                    company_phone TEXT,
                    company_email TEXT,
                    company_address TEXT,
                    company_logo TEXT,
                    theme TEXT,
                    currency TEXT,
                    backup_dir TEXT,
                    reports_dir TEXT,
                    setup_complete INTEGER DEFAULT 0
                )
            """)

            # Inserir configurações da empresa
            cursor.execute("""
                INSERT INTO config (
                    company_name, company_cnpj, company_phone, company_email,
                    company_address, company_logo, theme, currency,
                    backup_dir, reports_dir, setup_complete
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                self.company_name.get(),
                ''.join(filter(str.isdigit, self.company_cnpj.get())),
                self.company_phone.get(),
                self.company_email.get(),
                self.company_address.get("1.0", "end-1c"),
                self.logo_path.get(),
                self.theme_choice.get(),
                self.currency.get(),
                self.backup_dir.get(),
                self.reports_dir.get()
            ))

            # Criar conta do administrador
            hashed_password = hashlib.sha256(self.admin_password.get().encode()).hexdigest()

            cursor.execute("""
                INSERT INTO funcionarios (
                    nome, cpf, email, usuario, senha, is_admin, cargo, salario
                ) VALUES (?, ?, ?, ?, ?, 1, 'Administrador', 0)
            """, (
                self.admin_name.get(),
                ''.join(filter(str.isdigit, self.admin_cpf.get())),
                self.admin_email.get(),
                self.admin_username.get(),
                hashed_password
            ))

            # Criar diretórios necessários
            os.makedirs(self.backup_dir.get(), exist_ok=True)
            os.makedirs(self.reports_dir.get(), exist_ok=True)

            self.conn.commit()

            messagebox.showinfo(
                "Configuração Completa",
                "Sistema configurado com sucesso!\n\n"
                f"Use o usuário '{self.admin_username.get()}' para fazer login."
            )

            self.setup_window.destroy()
            self.on_setup_complete()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha na configuração inicial:\n{str(e)}")

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()