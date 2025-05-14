import ttkbootstrap as ttk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from modules.models.database import create_connection


class DashboardModule:
    def __init__(self, parent):
        self.parent = parent
        self.conn = create_connection()
        self.create_widgets()
        self.update_metrics()

    def create_widgets(self):
        """Cria a interface do dashboard"""
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Cards de métricas
        metrics_frame = ttk.Frame(self.main_frame)
        metrics_frame.pack(fill="x", pady=(0, 20))

        self.cards = {
            'alugueis': self.create_metric_card(metrics_frame, "Aluguéis Ativos", "0", "primary"),
            'receita': self.create_metric_card(metrics_frame, "Receita Mensal", "R$ 0", "success"),
            'clientes': self.create_metric_card(metrics_frame, "Novos Clientes", "0", "info"),
            'estoque': self.create_metric_card(metrics_frame, "Itens Disponível", "0", "warning")
        }

        # Gráficos
        graphs_frame = ttk.Frame(self.main_frame)
        graphs_frame.pack(fill="both", expand=True)

        # Gráfico 1: Aluguéis por mês
        fig1 = Figure(figsize=(5, 4), dpi=100)
        self.ax1 = fig1.add_subplot(111)
        self.canvas1 = FigureCanvasTkAgg(fig1, master=graphs_frame)
        self.canvas1.get_tk_widget().pack(side="left", fill="both", expand=True, padx=5)

        # Gráfico 2: Itens mais alugados
        fig2 = Figure(figsize=(5, 4), dpi=100)
        self.ax2 = fig2.add_subplot(111)
        self.canvas2 = FigureCanvasTkAgg(fig2, master=graphs_frame)
        self.canvas2.get_tk_widget().pack(side="left", fill="both", expand=True, padx=5)

        # Botão de atualização
        ttk.Button(
            self.main_frame,
            text="Atualizar Dados",
            bootstyle="light",
            command=self.update_metrics
        ).pack(pady=10)

    def create_metric_card(self, parent, title, value, style):
        """Cria um card de métrica"""
        card = ttk.Frame(parent, bootstyle=style, padding=10)
        card.pack(side="left", expand=True, fill="x", padx=5)

        ttk.Label(card, text=title, bootstyle=f"{style}-inverse").pack()
        value_label = ttk.Label(card, text=value, font=('Helvetica', 14, 'bold'))
        value_label.pack(pady=5)

        return value_label

    def update_metrics(self):
        """Atualiza todas as métricas e gráficos"""
        try:
            cursor = self.conn.cursor()

            # Aluguéis ativos
            cursor.execute("SELECT COUNT(*) FROM alugueis WHERE status='ativo'")
            self.cards['alugueis'].config(text=str(cursor.fetchone()[0]))

            # Receita mensal
            cursor.execute("""
                SELECT SUM(valor) FROM pagamentos 
                WHERE strftime('%m', data_pagamento) = strftime('%m', 'now')
            """)
            receita = cursor.fetchone()[0] or 0
            self.cards['receita'].config(text=f"R$ {receita:.2f}")

            # Novos clientes
            cursor.execute("""
                SELECT COUNT(*) FROM clientes 
                WHERE strftime('%m', data_cadastro) = strftime('%m', 'now')
            """)
            self.cards['clientes'].config(text=str(cursor.fetchone()[0]))

            # Itens disponíveis
            cursor.execute("SELECT SUM(quantidade) FROM estoque WHERE status='disponivel'")
            self.cards['estoque'].config(text=str(cursor.fetchone()[0] or 0))

            # Gráfico 1: Aluguéis por mês
            cursor.execute("""
                SELECT strftime('%m/%Y', data_inicio), COUNT(*) 
                FROM alugueis 
                GROUP BY strftime('%m/%Y', data_inicio)
                ORDER BY data_inicio DESC LIMIT 6
            """)
            meses, valores = zip(*reversed(cursor.fetchall()))
            self.ax1.clear()
            self.ax1.bar(meses, valores, color='skyblue')
            self.ax1.set_title('Aluguéis por Mês')
            self.ax1.tick_params(axis='x', rotation=45)
            self.canvas1.draw()

            # Gráfico 2: Itens mais alugados
            cursor.execute("""
                SELECT e.nome, COUNT(ia.id) 
                FROM itens_aluguel ia
                JOIN estoque e ON ia.item_id = e.id
                GROUP BY e.nome 
                ORDER BY COUNT(ia.id) DESC 
                LIMIT 5
            """)
            itens, quantidades = zip(*cursor.fetchall())
            self.ax2.clear()
            self.ax2.pie(quantidades, labels=itens, autopct='%1.1f%%')
            self.ax2.set_title('Itens Mais Alugados')
            self.canvas2.draw()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar dashboard: {str(e)}")
