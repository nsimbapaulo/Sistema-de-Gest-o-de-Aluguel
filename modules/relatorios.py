import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from .database import create_connection
from datetime import datetime
import webbrowser
from jinja2 import Template
import os


class RelatoriosModule:
    def __init__(self, parent):
        self.parent = parent
        self.conn = create_connection()
        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame de relatórios
        reports_frame = ttk.LabelFrame(self.main_frame, text="Gerar Relatórios", bootstyle="info")
        reports_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Botões de relatórios
        btn1 = ttk.Button(
            reports_frame,
            text="Relatório de Aluguéis por Período",
            bootstyle="primary",
            command=self.relatorio_alugueis_periodo,
            width=30
        )
        btn1.pack(pady=10)

        btn2 = ttk.Button(
            reports_frame,
            text="Relatório de Itens Mais Alugados",
            bootstyle="primary",
            command=self.relatorio_itens_mais_alugados,
            width=30
        )
        btn2.pack(pady=10)

        btn3 = ttk.Button(
            reports_frame,
            text="Relatório Financeiro Mensal",
            bootstyle="primary",
            command=self.relatorio_financeiro_mensal,
            width=30
        )
        btn3.pack(pady=10)

        btn4 = ttk.Button(
            reports_frame,
            text="Relatório de Clientes",
            bootstyle="primary",
            command=self.relatorio_clientes,
            width=30
        )
        btn4.pack(pady=10)

    def relatorio_alugueis_periodo(self):
        """Gera relatório de aluguéis por período"""
        self.report_window = ttk.Toplevel(self.parent)
        self.report_window.title("Relatório de Aluguéis por Período")

        # Frame de filtros
        filter_frame = ttk.Frame(self.report_window)
        filter_frame.pack(padx=10, pady=10)

        ttk.Label(filter_frame, text="Data Início:").grid(row=0, column=0, sticky="e", pady=5)
        self.start_date_entry = ttk.DateEntry(filter_frame)
        self.start_date_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(filter_frame, text="Data Fim:").grid(row=1, column=0, sticky="e", pady=5)
        self.end_date_entry = ttk.DateEntry(filter_frame)
        self.end_date_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(filter_frame, text="Status:").grid(row=2, column=0, sticky="e", pady=5)
        self.status_combobox = ttk.Combobox(
            filter_frame,
            values=["Todos", "ativo", "concluido", "atrasado"]
        )
        self.status_combobox.grid(row=2, column=1, pady=5, padx=5)
        self.status_combobox.current(0)

        # Botões
        btn_frame = ttk.Frame(self.report_window)
        btn_frame.pack(pady=10)

        generate_btn = ttk.Button(
            btn_frame,
            text="Gerar Relatório",
            bootstyle="success",
            command=self.generate_relatorio_alugueis
        )
        generate_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancelar",
            bootstyle="danger",
            command=self.report_window.destroy
        )
        cancel_btn.pack(side="left", padx=5)

    def generate_relatorio_alugueis(self):
        """Gera o relatório HTML de aluguéis"""
        try:
            start_date = datetime.strptime(self.start_date_entry.entry.get(), "%m/%d/%Y").strftime("%Y-%m-%d")
            end_date = datetime.strptime(self.end_date_entry.entry.get(), "%m/%d/%Y").strftime("%Y-%m-%d")
            status = self.status_combobox.get()
        except ValueError:
            messagebox.showerror("Erro", "Data inválida! Use o formato MM/DD/AAAA")
            return

        cursor = self.conn.cursor()

        if status == "Todos":
            cursor.execute("""
                SELECT a.id, c.nome AS cliente, f.nome AS funcionario, 
                       a.data_inicio, a.data_devolucao, a.status, a.valor_total
                FROM alugueis a
                JOIN clientes c ON a.cliente_id = c.id
                JOIN funcionarios f ON a.funcionario_id = f.id
                WHERE a.data_inicio BETWEEN ? AND ?
                ORDER BY a.data_inicio
            """, (start_date, end_date))
        else:
            cursor.execute("""
                SELECT a.id, c.nome AS cliente, f.nome AS funcionario, 
                       a.data_inicio, a.data_devolucao, a.status, a.valor_total
                FROM alugueis a
                JOIN clientes c ON a.cliente_id = c.id
                JOIN funcionarios f ON a.funcionario_id = f.id
                WHERE a.data_inicio BETWEEN ? AND ? AND a.status = ?
                ORDER BY a.data_inicio
            """, (start_date, end_date, status))

        alugueis = cursor.fetchall()

        # Obter total
        total = sum(a[6] for a in alugueis) if alugueis else 0

        # Gerar HTML
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Relatório de Aluguéis</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                .header { text-align: center; margin-bottom: 20px; }
                .info { margin-bottom: 20px; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .total { text-align: right; font-weight: bold; font-size: 1.1em; }
                .footer { margin-top: 30px; text-align: center; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Relatório de Aluguéis</h1>
                <p>Período: {{ data_inicio }} a {{ data_fim }} | Status: {{ status }}</p>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Cliente</th>
                        <th>Funcionário</th>
                        <th>Data Início</th>
                        <th>Data Devolução</th>
                        <th>Status</th>
                        <th>Valor Total</th>
                    </tr>
                </thead>
                <tbody>
                    {% for aluguel in alugueis %}
                    <tr>
                        <td>{{ aluguel[0] }}</td>
                        <td>{{ aluguel[1] }}</td>
                        <td>{{ aluguel[2] }}</td>
                        <td>{{ aluguel[3] }}</td>
                        <td>{{ aluguel[4] }}</td>
                        <td>{{ aluguel[5] }}</td>
                        <td>R$ {{ "%.2f"|format(aluguel[6]) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

            <div class="total">
                <p>Total: R$ {{ "%.2f"|format(total) }}</p>
            </div>

            <div class="footer">
                <p>Relatório gerado em {{ data_geracao }}</p>
            </div>
        </body>
        </html>
        """

        template = Template(template_str)
        data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")

        html = template.render(
            data_inicio=start_date,
            data_fim=end_date,
            status=status,
            alugueis=alugueis,
            total=total,
            data_geracao=data_geracao
        )

        # Salvar e abrir relatório
        if not os.path.exists("relatorios"):
            os.makedirs("relatorios")

        file_path = "relatorios/relatorio_alugueis.html"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open(f"file://{os.path.abspath(file_path)}")
        self.report_window.destroy()

    def relatorio_itens_mais_alugados(self):
        """Gera relatório de itens mais alugados"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT e.nome, COUNT(ia.id) AS total_alugueis, 
                   SUM(ia.quantidade) AS total_itens, 
                   SUM(ia.quantidade * ia.valor_unitario) AS total_valor
            FROM itens_aluguel ia
            JOIN estoque e ON ia.item_id = e.id
            JOIN alugueis a ON ia.aluguel_id = a.id
            GROUP BY e.nome
            ORDER BY total_itens DESC
            LIMIT 10
        """)
        itens = cursor.fetchall()

        total_itens = sum(i[2] for i in itens) if itens else 0
        total_valor = sum(i[3] for i in itens) if itens else 0

        # Gerar HTML
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Itens Mais Alugados</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                .header { text-align: center; margin-bottom: 20px; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .total { text-align: right; font-weight: bold; }
                .footer { margin-top: 30px; text-align: center; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Itens Mais Alugados</h1>
                <p>Top 10 itens mais alugados</p>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Total de Aluguéis</th>
                        <th>Total de Itens</th>
                        <th>Valor Total</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in itens %}
                    <tr>
                        <td>{{ item[0] }}</td>
                        <td>{{ item[1] }}</td>
                        <td>{{ item[2] }}</td>
                        <td>R$ {{ "%.2f"|format(item[3]) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

            <div class="total">
                <p>Total de Itens: {{ total_itens }}</p>
                <p>Valor Total: R$ {{ "%.2f"|format(total_valor) }}</p>
            </div>

            <div class="footer">
                <p>Relatório gerado em {{ data_geracao }}</p>
            </div>
        </body>
        </html>
        """

        template = Template(template_str)
        data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")

        html = template.render(
            itens=itens,
            total_itens=total_itens,
            total_valor=total_valor,
            data_geracao=data_geracao
        )

        # Salvar e abrir relatório
        if not os.path.exists("relatorios"):
            os.makedirs("relatorios")

        file_path = "relatorios/relatorio_itens_mais_alugados.html"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open(f"file://{os.path.abspath(file_path)}")

    def relatorio_financeiro_mensal(self):
        """Gera relatório financeiro mensal"""
        self.finance_window = ttk.Toplevel(self.parent)
        self.finance_window.title("Relatório Financeiro Mensal")

        # Frame de filtros
        filter_frame = ttk.Frame(self.finance_window)
        filter_frame.pack(padx=10, pady=10)

        ttk.Label(filter_frame, text="Ano:").grid(row=0, column=0, sticky="e", pady=5)
        self.ano_combobox = ttk.Combobox(
            filter_frame,
            values=[str(year) for year in range(2020, datetime.now().year + 1)]
        )
        self.ano_combobox.grid(row=0, column=1, pady=5, padx=5)
        self.ano_combobox.set(str(datetime.now().year))

        ttk.Label(filter_frame, text="Mês:").grid(row=1, column=0, sticky="e", pady=5)
        self.mes_combobox = ttk.Combobox(
            filter_frame,
            values=[
                "Todos", "Janeiro", "Fevereiro", "Março", "Abril",
                "Maio", "Junho", "Julho", "Agosto",
                "Setembro", "Outubro", "Novembro", "Dezembro"
            ]
        )
        self.mes_combobox.grid(row=1, column=1, pady=5, padx=5)
        self.mes_combobox.set("Todos")

        # Botões
        btn_frame = ttk.Frame(self.finance_window)
        btn_frame.pack(pady=10)

        generate_btn = ttk.Button(
            btn_frame,
            text="Gerar Relatório",
            bootstyle="success",
            command=self.generate_relatorio_financeiro
        )
        generate_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancelar",
            bootstyle="danger",
            command=self.finance_window.destroy
        )
        cancel_btn.pack(side="left", padx=5)

    def generate_relatorio_financeiro(self):
        """Gera o relatório financeiro"""
        ano = self.ano_combobox.get()
        mes = self.mes_combobox.get()

        if not ano:
            messagebox.showerror("Erro", "Selecione um ano!")
            return

        cursor = self.conn.cursor()

        if mes == "Todos":
            # Relatório anual
            cursor.execute("""
                SELECT strftime('%m', p.data_pagamento) AS mes,
                       COUNT(p.id) AS total_alugueis,
                       SUM(p.valor) AS total_receita
                FROM pagamentos p
                WHERE strftime('%Y', p.data_pagamento) = ?
                GROUP BY strftime('%m', p.data_pagamento)
                ORDER BY mes
            """, (ano,))

            dados = cursor.fetchall()

            # Mapear números de mês para nomes
            meses_nome = [
                "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
            ]

            dados_formatados = []
            for mes_num, total_alugueis, total_receita in dados:
                mes_nome = meses_nome[int(mes_num) - 1]
                dados_formatados.append((mes_nome, total_alugueis, total_receita))

            titulo = f"Relatório Financeiro Anual - {ano}"
            colunas = ["Mês", "Total de Aluguéis", "Total Receita"]
            total_receita = sum(d[2] for d in dados_formatados) if dados_formatados else 0
        else:
            # Relatório mensal
            mes_num = meses_nome.index(mes) + 1
            cursor.execute("""
                SELECT a.id, c.nome, p.valor, p.data_pagamento, p.metodo
                FROM pagamentos p
                JOIN alugueis a ON p.aluguel_id = a.id
                JOIN clientes c ON a.cliente_id = c.id
                WHERE strftime('%Y', p.data_pagamento) = ? 
                AND strftime('%m', p.data_pagamento) = ?
                ORDER BY p.data_pagamento
            """, (ano, f"{mes_num:02d}"))

            dados = cursor.fetchall()
            titulo = f"Relatório Financeiro - {mes}/{ano}"
            colunas = ["ID Aluguel", "Cliente", "Valor", "Data Pagamento", "Método"]
            total_receita = sum(d[2] for d in dados) if dados else 0

        # Gerar HTML
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{{ titulo }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                .header { text-align: center; margin-bottom: 20px; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .total { text-align: right; font-weight: bold; font-size: 1.1em; }
                .footer { margin-top: 30px; text-align: center; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ titulo }}</h1>
            </div>

            <table>
                <thead>
                    <tr>
                        {% for coluna in colunas %}
                        <th>{{ coluna }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for linha in dados %}
                    <tr>
                        {% for item in linha %}
                        <td>
                            {% if loop.index0 == 2 or loop.index0 == 4 %}
                                R$ {{ "%.2f"|format(item) }}
                            {% else %}
                                {{ item }}
                            {% endif %}
                        </td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

            <div class="total">
                <p>Total Receita: R$ {{ "%.2f"|format(total_receita) }}</p>
            </div>

            <div class="footer">
                <p>Relatório gerado em {{ data_geracao }}</p>
            </div>
        </body>
        </html>
        """

        template = Template(template_str)
        data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")

        html = template.render(
            titulo=titulo,
            colunas=colunas,
            dados=dados_formatados if mes == "Todos" else dados,
            total_receita=total_receita,
            data_geracao=data_geracao
        )

        # Salvar e abrir relatório
        if not os.path.exists("relatorios"):
            os.makedirs("relatorios")

        file_name = f"relatorio_financeiro_{mes.lower()}_{ano}.html"
        file_path = f"relatorios/{file_name}"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open(f"file://{os.path.abspath(file_path)}")
        self.finance_window.destroy()

    def relatorio_clientes(self):
        """Gera relatório de clientes"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT nome, bi, telefone, email, data_cadastro
            FROM clientes
            ORDER BY nome
        """)
        clientes = cursor.fetchall()

        # Gerar HTML
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Relatório de Clientes</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                .header { text-align: center; margin-bottom: 20px; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .footer { margin-top: 30px; text-align: center; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Relatório de Clientes</h1>
                <p>Total de clientes: {{ total_clientes }}</p>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>BI</th>
                        <th>Telefone</th>
                        <th>E-mail</th>
                        <th>Data Cadastro</th>
                    </tr>
                </thead>
                <tbody>
                    {% for cliente in clientes %}
                    <tr>
                        <td>{{ cliente[0] }}</td>
                        <td>{{ cliente[1] }}</td>
                        <td>{{ cliente[2] }}</td>
                        <td>{{ cliente[3] }}</td>
                        <td>{{ cliente[4] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

            <div class="footer">
                <p>Relatório gerado em {{ data_geracao }}</p>
            </div>
        </body>
        </html>
        """

        template = Template(template_str)
        data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")

        html = template.render(
            clientes=clientes,
            total_clientes=len(clientes),
            data_geracao=data_geracao
        )

        # Salvar e abrir relatório
        if not os.path.exists("relatorios"):
            os.makedirs("relatorios")

        file_path = "relatorios/relatorio_clientes.html"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open(f"file://{os.path.abspath(file_path)}")

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()