import ttkbootstrap as ttk
from tkinter import messagebox
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import *
from modules.models.database import create_connection
from datetime import datetime
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

            valor_total, cliente_nome, cliente_bi, cliente_endereco = aluguel_info

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
            self.gerar_pdf_fatura(
                aluguel_id,
                cliente_nome,
                cliente_bi,
                cliente_endereco,
                metodo_pagamento,
                itens,
                valor_total
            )

            messagebox.showinfo("Sucesso", "Fatura gerada com sucesso!")
            self.generate_window.destroy()
            self.load_faturas()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar fatura: {str(e)}")

    def gerar_pdf_fatura(self, alugel_id, cliente_nome, cliente_bi, cliente_endereco, metodo_pagamento, itens, valor_total):
        try:
            def cm_ponto(milimetros: float):
                """
                Essa função converte milímtros para ponos
                :param milimetros: valor em milímetros
                :return: valor em pontos
                """
                return round(10 * (milimetros * 2.83464567))

            doc_name = f'factura {alugel_id}'
            doc = f"Facturas/{doc_name}.pdf"
            datetime.now().strftime("%d/%m/%Y %H:%M")

            os.makedirs(os.path.dirname(doc), exist_ok=True)
            w, h = A4
            const = 50
            canva = canvas.Canvas(doc, pagesize=A4)

            # Logotipo da empresa
            canva.setFont('Helvetica-Bold', 20)
            canva.drawString(w - 100, h - 60, "Logo")

            # Numero da factura
            canva.drawString(const, h - (const + cm_ponto(2.5)), f"Fatura nº: {alugel_id}")

            # Dados do cliente
            texto = canva.beginText(const, h - (const + cm_ponto(3)))
            texto.setFont("Courier", 11)
            texto.textLine(f"Nome: {cliente_nome}")
            texto.textLine(f"B.I: {cliente_bi}")
            texto.textLine(f"Endereço: {cliente_endereco}")
            texto.textLine(f"Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}")
            texto.textLine(f"Método de Pagamento: {metodo_pagamento}")

            canva.drawText(texto)

            # Cabeçalho da tabela
            canva.setFont('Helvetica-Bold', 11)
            canva.setFillColor(black)  # cor dos rectangulos
            canva.rect(const, h - (const + cm_ponto(6)), cm_ponto(7), cm_ponto(0.5), fill=1)
            canva.rect((const + cm_ponto(7.6)), h - (const + cm_ponto(6)), cm_ponto(3), cm_ponto(0.5), fill=1)
            canva.rect((const + cm_ponto(11.2)), h - (const + cm_ponto(6)), cm_ponto(3), cm_ponto(0.5), fill=1)
            canva.rect((const + cm_ponto(14.7)), h - (const + cm_ponto(6)), cm_ponto(2.5), cm_ponto(0.5), fill=1)

            canva.setFillColor(white)  # cor das letrsa
            canva.drawString(const + cm_ponto(1.9), h - (const + cm_ponto(5.9)), "Item")
            canva.drawString((const + cm_ponto(7.9)), h - (const + cm_ponto(5.9)), "Quantidade")
            canva.drawString((const + cm_ponto(11.9)), h - (const + cm_ponto(5.9)), "Unidade")
            canva.drawString((const + cm_ponto(15.3)), h - (const + cm_ponto(5.9)), "Total")

            # Dados da Tabela
            canva.setFillColor(black)  # cor das letrsa
            canva.setFont('Helvetica', 11)

            expaco = 6.5
            expaco_ = 6.6
            add = 0.5
            for item in itens:
                canva.drawString(const + cm_ponto(0.1), h - (const + cm_ponto(expaco)), f"{item[0]}")
                canva.drawString((const + cm_ponto(8.7)), h - (const + cm_ponto(expaco)), f"{item[1]}")
                canva.drawString((const + cm_ponto(12.2)), h - (const + cm_ponto(expaco)), f"{item[2]}")
                canva.drawString((const + cm_ponto(15.3)), h - (const + cm_ponto(expaco)), f"{item[1] * item[2]}")
                canva.line(const, h - (const + cm_ponto(expaco_)), cm_ponto(19), h - (const + cm_ponto(expaco_)))

                expaco += add
                expaco_ += add

            canva.setFont("Helvetica-Bold", 12, )
            canva.drawString((const + cm_ponto(13.7)), h - (const + cm_ponto(expaco + add)), f"Total: {valor_total} kz")

            canva.showPage()
            canva.save()

            webbrowser.open_new(f"file://{os.path.abspath(doc)}")

            return doc
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar PDF:. {str(e)}")
            return None

    def print_fatura(self):
        """Imprime a fatura selecionada"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma fatura para imprimir!")
            return

        item = self.tree.item(selected)
        fatura_id = item['values'][0]

        file_path = f"Facturas/factura {fatura_id}.pdf"
        if os.path.exists(file_path):
            webbrowser.open(f"file://{os.path.abspath(file_path)}")
        else:
            messagebox.showerror("Erro", "Arquivo da fatura não encontrado!")

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()