import ttkbootstrap as ttk
from tkinter import messagebox
from modules.clientes import ClientesModule
from modules.funcionarios import FuncionariosModule
from modules.estoque import EstoqueModule
from modules.alugueis import AlugueisModule
from modules.financeiro import FinanceiroModule
from modules.relatorios import RelatoriosModule
from modules.notificacoes import NotificacoesModule
from modules.models.database import create_connection, initialize_database
from modules.auth import AuthSystem
from modules.setup import FirstRunSetup
from modules.dashboard import DashboardModule


class MainApplication(ttk.Window):
    def __init__(self):
        super().__init__(themename="superhero")

        self.title("Sistema de Gestão de Aluguel")
        self.geometry("1200x700")
        self.current_user = None

        # Verificar se é a primeira execução
        self.conn = create_connection()
        self.check_first_run()

    def check_first_run(self):
        """Verifica se é a primeira execução do sistema"""
        cursor = self.conn.cursor()

        try:
            # Verificar se a tabela de configuração existe e está completa
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='config'
            """)

            if not cursor.fetchone():
                # Tabela não existe, é a primeira execução
                self.show_setup_wizard()
                return

            cursor.execute("SELECT setup_complete FROM config LIMIT 1")
            result = cursor.fetchone()

            if not result or not result[0]:
                self.show_setup_wizard()
            else:
                self.show_login()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao verificar configuração:\n{str(e)}")
            self.destroy()

    def show_setup_wizard(self):
        """Mostra o assistente de configuração inicial"""
        self.withdraw()  # Esconde a janela principal

        # Inicializar banco de dados
        initialize_database()

        # Mostrar assistente de configuração
        FirstRunSetup(self, self.show_login)

    def show_login(self):
        """Mostra a tela de login"""
        self.withdraw()  # Garante que a janela principal está escondida

        # Carregar configuração do tema
        cursor = self.conn.cursor()
        cursor.execute("SELECT theme FROM config LIMIT 1")
        result = cursor.fetchone()
        theme = result[0] if result else "superhero"

        # Aplicar tema
        self.style.theme_use(theme)

        # Mostrar sistema de autenticação
        AuthSystem(self, self.on_login_success)

    # ... (restante do código permanece igual)

    def on_login_success(self, user_data):
        """Callback chamado após login bem-sucedido"""
        self.current_user = user_data
        self.deiconify()  # Mostrar a janela principal
        self.create_widgets()

        # Atualizar título com nome do usuário
        self.title(f"Sistema de Gestão de Aluguel - {user_data['nome']}")

        # Configurar barra de status
        self.status_bar.config(
            text=f"Usuário: {user_data['nome']} | Nível: {'Administrador' if user_data['is_admin'] else 'Funcionário'}")

    def create_widgets(self):
        """Cria os widgets da interface principal"""
        # Barra de navegação lateral
        self.nav_frame = ttk.Frame(self, width=200, bootstyle="dark")
        self.nav_frame.pack(side="left", fill="y")

        # Área de conteúdo principal
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(side="right", expand=True, fill="both")

        # Botões de navegação (apenas módulos permitidos)
        buttons = []

        # Módulos básicos para todos os usuários
        buttons.append(("Aluguéis", "cart", self.show_alugueis))
        buttons.append(("Dashboard", "speedometer2", self.show_dashboard))

        # Módulos restritos para administradores
        if self.current_user['is_admin']:
            buttons.extend([
                ("Clientes", "person", self.show_clientes),
                ("Funcionários", "people", self.show_funcionarios),
                ("Estoque", "box-seam", self.show_estoque),
                ("Financeiro", "currency-dollar", self.show_financeiro),
                ("Relatórios", "clipboard-data", self.show_relatorios),
                ("Notificações", "bell", self.show_notificacoes),
            ])

        for text, icon, command in buttons:
            btn = ttk.Button(
                self.nav_frame,
                text=text,
                bootstyle="light-outline",
                command=command,
                width=15
            )
            btn.pack(pady=5, padx=10, ipady=5)

        # Botão de logout
        logout_btn = ttk.Button(
            self.nav_frame,
            text="Sair",
            bootstyle="danger",
            command=self.logout,
            width=15
        )
        logout_btn.pack(side="bottom", pady=10, padx=10, ipady=5)


        # Barra de status
        self.status_bar = ttk.Label(self, bootstyle="inverse-dark")
        self.status_bar.pack(side="bottom", fill="x")

        # Mostrar dashboard inicial
        self.show_dashboard()

    def logout(self):
        """Realiza logout do sistema"""
        self.current_user = None
        self.destroy()

        # Reabrir aplicação
        app = MainApplication()
        app.mainloop()


    def show_dashboard(self):
        self.clear_content()
        DashboardModule(self.content_frame)

        # Adicione widgets do dashboard aqui

    def show_clientes(self):
        self.clear_content()
        ClientesModule(self.content_frame)

    def show_funcionarios(self):
        self.clear_content()
        FuncionariosModule(self.content_frame)

    def show_estoque(self):
        self.clear_content()
        EstoqueModule(self.content_frame)

    def show_alugueis(self):
        self.clear_content()
        AlugueisModule(self.content_frame)

    def show_financeiro(self):
        self.clear_content()
        FinanceiroModule(self.content_frame)

    def show_relatorios(self):
        self.clear_content()
        RelatoriosModule(self.content_frame)

    def show_notificacoes(self):
        self.clear_content()
        NotificacoesModule(self.content_frame)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop() 