import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from modules.clientes import ClientesModule
from modules.funcionarios import FuncionariosModule
from modules.estoque import EstoqueModule
from modules.alugueis import AlugueisModule
from modules.financeiro import FinanceiroModule
from modules.relatorios import RelatoriosModule
from modules.notificacoes import NotificacoesModule
from modules.database import create_connection, create_tables


class MainApplication(ttk.Window):
    def __init__(self):
        super().__init__(themename="superhero")

        self.title("Sistema de Gestão de Aluguel")
        self.geometry("1200x700")
        self.conn = create_connection()
        create_tables(self.conn)
        self.create_widgets()

    def create_widgets(self):
        # Barra de navegação lateral
        self.nav_frame = ttk.Frame(self, width=200, bootstyle="dark")
        self.nav_frame.pack(side="left", fill="y")

        # Área de conteúdo principal
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(side="right", expand=True, fill="both")

        # Botões de navegação
        buttons = [
            ("Clientes", "person", self.show_clientes),
            ("Funcionários", "people", self.show_funcionarios),
            ("Estoque", "box-seam", self.show_estoque),
            ("Aluguéis", "cart", self.show_alugueis),
            ("Financeiro", "currency-dollar", self.show_financeiro),
            ("Relatórios", "clipboard-data", self.show_relatorios),
            ("Notificações", "bell", self.show_notificacoes),
        ]

        for text, icon, command in buttons:
            btn = ttk.Button(
                self.nav_frame,
                text=text,
                bootstyle="light-outline",
                command=command,
                width=15
            )
            btn.pack(pady=5, padx=10, ipady=5)

        # Barra de status
        self.status_bar = ttk.Label(self, bootstyle="inverse-dark")
        self.status_bar.pack(side="bottom", fill="x")

        # Mostrar dashboard inicial
        self.show_dashboard()

    def show_dashboard(self):
        self.clear_content()
        label = ttk.Label(self.content_frame, text="Dashboard", font=('Helvetica', 18))
        label.pack(pady=20)

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