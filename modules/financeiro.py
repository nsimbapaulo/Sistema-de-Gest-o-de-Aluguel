import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from .database import create_connection
from datetime import datetime
from jinja2 import Template
import webbrowser
import os


class FinanceiroModule:
    def __init__(self, parent):
        self.parent = parent
        self.conn = create_connection()
        self.create_widgets()
        self.load_faturas()

    def create_widgets(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame de filtros
        filter_frame = ttk.LabelFrame(self.main_frame, text="Filtrar Faturas", bootstyle="info")
        filter_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(filter_frame, text="Período:").pack(side="left", padx=5)

        self.start_date_entry = ttk.DateEntry(filter_frame)
        self.start_date_entry.pack(side="left", padx=5)

        ttk.Label(filter_frame, text="até").pack(side="left", padx=5)

        self.end_date_entry = ttk.DateEntry(filter_frame)
        self.end_date_entry.pack(side="left", padx=5)

        filter_btn = ttk.Button(
            filter_frame,
            text="Filtrar",
            bootstyle="info-outline",
            command=self.filter_faturas
        )
        filter_btn.pack(side="left", padx=5)

        # Frame de ações
        actions_frame = ttk.Frame(self.main_frame)
        actions_frame.pack(fill="x", pady=(0, 10))

        generate_btn = ttk.Button(
            actions_frame,
            text="Gerar Fatura",
            bootstyle="success",
            command=self.open_generate_fatura
        )
        generate_btn.pack(side="left", padx=5)

        print_btn = ttk.Button(
            actions_frame,
            text="Imprimir Fatura",
            bootstyle="primary",
            command=self.print_fatura
        )
        print_btn.pack(side="left", padx=5)

        # Tabela de faturas
        columns = ("id", "aluguel_id", "cliente", "valor", "data_emissao", "status")
        self.tree = ttk.Treeview(
            self.main_frame,
            columns=columns,
            show="headings",
            bootstyle="dark",
            selectmode="browse"
        )

        self.tree.heading("id", text="ID Fatura")
        self.tree.heading("aluguel_id", text="ID Aluguel")
        self.tree.heading("cliente", text="Cliente")
        self.tree.heading("valor", text="Valor")
        self.tree.heading("data_emissao", text="Data Emissão")
        self.tree.heading("status", text="Status")

        self.tree.column("id", width=80)
        self.tree.column("aluguel_id", width=80)
        self.tree.column("cliente", width=200)
        self.tree.column("valor", width=100)
        self.tree.column("data_emissao", width=120)
        self.tree.column("status", width=100)

        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_faturas(self):
        """Carrega todas as faturas na tabela"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.id, p.aluguel_id, c.nome, p.valor, p.data_pagamento, p.status 
            FROM pagamentos p
            JOIN alugueis a ON p.aluguel_id = a.id
            JOIN clientes c ON a.cliente_id = c.id
            ORDER BY p.data_pagamento DESC
        """)
        rows = cursor.fetchall()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=row)

    def filter_faturas(self):
        """Filtra faturas por período"""
        start_date = self.start_date_entry.entry.get()
        end_date = self.end_date_entry.entry.get()

        try:
            start_date = datetime.strptime(start_date, "%m/%d/%Y").strftime("%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido! Use MM/DD/AAAA")
            return

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.id, p.aluguel_id, c.nome, p.valor, p.data_pagamento, p.status 
            FROM pagamentos p
            JOIN alugueis a ON p.aluguel_id = a.id
            JOIN clientes c ON a.cliente_id = c.id
            WHERE p.data_pagamento BETWEEN ? AND ?
            ORDER BY p.data_pagamento DESC
        """, (start_date, end_date))

        rows = cursor.fetchall()
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=row)

    def open_generate_fatura(self):
        """Abre janela para gerar nova fatura"""
        self.generate_window = ttk.Toplevel(self.parent)
        self.generate_window.title("Gerar Fatura")

        # Frame principal
        main_frame = ttk.Frame(self.generate_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Selecionar aluguel
        ttk.Label(main_frame, text="Aluguel:").grid(row=0, column=0, sticky="e", pady=5)

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT a.id, c.nome, a.data_inicio 
            FROM alugueis a
            JOIN clientes c ON a.cliente_id = c.id
            WHERE a.status = 'ativo'
        """)
        alugueis = cursor.fetchall()

        aluguel_options = [f"{a[0]} - {a[1]} ({a[2]})" for a in alugueis]

        self.aluguel_combobox = ttk.Combobox(main_frame, values=aluguel_options)
        self.aluguel_combobox.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        if aluguel_options:
            self.aluguel_combobox.current(0)
        else:
            messagebox.showwarning("Aviso", "Nenhum aluguel ativo encontrado!")
            self.generate_window.destroy()
            return

        # Método de pagamento
        ttk.Label(main_frame, text="Método de Pagamento:").grid(row=1, column=0, sticky="e", pady=5)
        self.metodo_combobox = ttk.Combobox(
            main_frame,
            values=["Dinheiro", "Cartão Crédito", "Cartão Débito", "Transferência", "PIX"]
        )
        self.metodo_combobox.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
        self.metodo_combobox.current(0)

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)

        generate_btn = ttk.Button(
            btn_frame,
            text="Gerar Fatura",
            bootstyle="success",
            command=self.generate_fatura
        )
        generate_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancelar",
            bootstyle="danger",
            command=self.generate_window.destroy
        )
        cancel_btn.pack(side="left", padx=5)

    def generate_fatura(self):
        """Gera uma nova fatura"""
        aluguel_selecionado = self.aluguel_combobox.get()
        if not aluguel_selecionado:
            messagebox.showerror("Erro", "Selecione um aluguel!")
            return

        aluguel_id = int(aluguel_selecionado.split(" - ")[0])
        metodo_pagamento = self.metodo_combobox.get()

        try:
            cursor = self.conn.cursor()

            # Obter informações do aluguel
            cursor.execute("""
                SELECT a.valor_total, c.nome, c.bi, c.endereco
                FROM alugueis a
                JOIN clientes c ON a.cliente_id = c.id
                WHERE a.id = ?
            """, (aluguel_id,))
            aluguel_info = cursor.fetchone()

            if not aluguel_info:
                messagebox.showerror("Erro", "Aluguel não encontrado!")
                return

            valor_total, cliente_nome, cliente_cpf, cliente_endereco = aluguel_info

            # Obter itens do aluguel
            cursor.execute("""
                SELECT e.nome, ia.quantidade, ia.valor_unitario
                FROM itens_aluguel ia
                JOIN estoque e ON ia.item_id = e.id
                WHERE ia.aluguel_id = ?
            """, (aluguel_id,))
            itens = cursor.fetchall()

            # Inserir pagamento
            cursor.execute("""
                INSERT INTO pagamentos (
                    aluguel_id, valor, data_pagamento, metodo, status
                ) VALUES (?, ?, datetime('now'), ?, 'pago')
            """, (aluguel_id, valor_total, metodo_pagamento))

            # Atualizar status do aluguel
            cursor.execute("""
                UPDATE alugueis SET status = 'concluido' WHERE id = ?
            """, (aluguel_id,))

            self.conn.commit()

            # Gerar HTML da fatura
            self.gerar_html_fatura(
                aluguel_id,
                cliente_nome,
                cliente_cpf,
                cliente_endereco,
                valor_total,
                itens,
                metodo_pagamento
            )

            messagebox.showinfo("Sucesso", "Fatura gerada com sucesso!")
            self.generate_window.destroy()
            self.load_faturas()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar fatura: {str(e)}")

    def gerar_html_fatura(self, aluguel_id, cliente_nome, cliente_cpf, cliente_endereco, valor_total, itens,
                          metodo_pagamento):
        """Gera um arquivo HTML com a fatura"""
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Fatura #{{ fatura_id }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                .header { text-align: center; margin-bottom: 20px; }
                .info { margin-bottom: 20px; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .total { text-align: right; font-weight: bold; }
                .footer { margin-top: 30px; text-align: center; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Fatura #{{ fatura_id }}</h1>
                <p>Sistema de Gestão de Aluguel</p>
            </div>

            <div class="info">
                <p><strong>Cliente:</strong> {{ cliente_nome }}</p>
                <p><strong>BI:</strong> {{ cliente_cpf }}</p>
                <p><strong>Endereço:</strong> {{ cliente_endereco }}</p>
                <p><strong>Data:</strong> {{ data_emissao }}</p>
                <p><strong>Método de Pagamento:</strong> {{ metodo_pagamento }}</p>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Quantidade</th>
                        <th>Valor Unitário</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in itens %}
                    <tr>
                        <td>{{ item[0] }}</td>
                        <td>{{ item[1] }}</td>
                        <td>R$ {{ "%.2f"|format(item[2]) }}</td>
                        <td>R$ {{ "%.2f"|format(item[1] * item[2]) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

            <div class="total">
                <p>Total: R$ {{ "%.2f"|format(valor_total) }}</p>
            </div>

            <div class="footer">
                <p>Obrigado por utilizar nossos serviços!</p>
                <p>Em caso de dúvidas, entre em contato conosco.</p>
            </div>
        </body>
        </html>
        """

        template = Template(template_str)
        data_emissao = datetime.now().strftime("%d/%m/%Y %H:%M")

        html = template.render(
            fatura_id=aluguel_id,
            cliente_nome=cliente_nome,
            cliente_cpf=cliente_cpf,
            cliente_endereco=cliente_endereco,
            data_emissao=data_emissao,
            valor_total=valor_total,
            itens=itens,
            metodo_pagamento=metodo_pagamento
        )

        # Criar diretório de faturas se não existir
        if not os.path.exists("faturas"):
            os.makedirs("faturas")

        file_path = f"faturas/fatura_{aluguel_id}.html"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)

        # Abrir no navegador
        webbrowser.open(f"file://{os.path.abspath(file_path)}")

    def print_fatura(self):
        """Imprime a fatura selecionada"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma fatura para imprimir!")
            return

        item = self.tree.item(selected)
        fatura_id = item['values'][0]

        file_path = f"faturas/fatura_{fatura_id}.html"
        if os.path.exists(file_path):
            webbrowser.open(f"file://{os.path.abspath(file_path)}")
        else:
            messagebox.showerror("Erro", "Arquivo da fatura não encontrado!")

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()