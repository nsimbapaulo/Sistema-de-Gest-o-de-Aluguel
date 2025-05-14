import ttkbootstrap as ttk
from tkinter import messagebox
from modules.models.database import create_connection
from datetime import datetime, timedelta


class AlugueisModule:
    def __init__(self, parent):
        self.parent = parent
        self.conn = create_connection()
        self.create_widgets()
        self.load_alugueis()

    def create_widgets(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame de filtros
        filter_frame = ttk.LabelFrame(self.main_frame, text="Filtrar Aluguéis", bootstyle="info")
        filter_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(filter_frame, text="Status:").pack(side="left", padx=5)
        self.status_combobox = ttk.Combobox(
            filter_frame,
            values=["Todos", "ativo", "concluido", "atrasado"]
        )
        self.status_combobox.pack(side="left", padx=5)
        self.status_combobox.current(0)

        filter_btn = ttk.Button(
            filter_frame,
            text="Filtrar",
            bootstyle="info-outline",
            command=self.filter_alugueis
        )
        filter_btn.pack(side="left", padx=5)

        # Frame de ações
        actions_frame = ttk.Frame(self.main_frame)
        actions_frame.pack(fill="x", pady=(0, 10))

        new_btn = ttk.Button(
            actions_frame,
            text="Novo Aluguel",
            bootstyle="success",
            command=self.open_new_aluguel
        )
        new_btn.pack(side="left", padx=5)

        devolver_btn = ttk.Button(
            actions_frame,
            text="Registrar Devolução",
            bootstyle="primary",
            command=self.registrar_devolucao
        )
        devolver_btn.pack(side="left", padx=5)

        # Tabela de aluguéis
        columns = ("id", "cliente", "funcionario", "data_inicio", "data_devolucao", "status", "valor_total")
        self.tree = ttk.Treeview(
            self.main_frame,
            columns=columns,
            show="headings",
            bootstyle="dark"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("cliente", text="Cliente")
        self.tree.heading("funcionario", text="Funcionário")
        self.tree.heading("data_inicio", text="Data Início")
        self.tree.heading("data_devolucao", text="Data Devolução")
        self.tree.heading("status", text="Status")
        self.tree.heading("valor_total", text="Valor Total")

        self.tree.column("id", width=50)
        self.tree.column("cliente", width=150)
        self.tree.column("funcionario", width=150)
        self.tree.column("data_inicio", width=100)
        self.tree.column("data_devolucao", width=100)
        self.tree.column("status", width=80)
        self.tree.column("valor_total", width=100)

        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configurar tags para status
        self.tree.tag_configure('ativo', background='#e6f3ff')
        self.tree.tag_configure('concluido', background='#e6ffe6')
        self.tree.tag_configure('atrasado', background='#ffebeb')

    def load_alugueis(self):
        """Carrega todos os aluguéis na tabela"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT a.id, c.nome, f.nome, a.data_inicio, a.data_devolucao, a.status, a.valor_total
            FROM alugueis a
            JOIN clientes c ON a.cliente_id = c.id
            JOIN funcionarios f ON a.funcionario_id = f.id
            ORDER BY a.data_inicio DESC
        """)
        rows = cursor.fetchall()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            valor_total = f"R$ {row[6]:.2f}" if row[6] else ""
            tags = (row[5],)  # Usa o status como tag
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], row[5], valor_total), tags=tags)

    def filter_alugueis(self):
        """Filtra aluguéis por status"""
        status = self.status_combobox.get()

        cursor = self.conn.cursor()
        if status == "Todos":
            cursor.execute("""
                SELECT a.id, c.nome, f.nome, a.data_inicio, a.data_devolucao, a.status, a.valor_total
                FROM alugueis a
                JOIN clientes c ON a.cliente_id = c.id
                JOIN funcionarios f ON a.funcionario_id = f.id
                ORDER BY a.data_inicio DESC
            """)
        else:
            cursor.execute("""
                SELECT a.id, c.nome, f.nome, a.data_inicio, a.data_devolucao, a.status, a.valor_total
                FROM alugueis a
                JOIN clientes c ON a.cliente_id = c.id
                JOIN funcionarios f ON a.funcionario_id = f.id
                WHERE a.status = ?
                ORDER BY a.data_inicio DESC
            """, (status,))

        rows = cursor.fetchall()
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            valor_total = f"R$ {row[6]:.2f}" if row[6] else ""
            tags = (row[5],)
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], row[5], valor_total), tags=tags)

    def open_new_aluguel(self):
        """Abre janela para criar novo aluguel"""
        self.new_window = ttk.Toplevel(self.parent)
        self.new_window.title("Novo Aluguel")

        # Frame principal
        main_frame = ttk.Frame(self.new_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame de seleção
        selection_frame = ttk.Frame(main_frame)
        selection_frame.pack(fill="x", pady=(0, 10))

        # Selecionar cliente
        ttk.Label(selection_frame, text="Cliente:").grid(row=0, column=0, sticky="e", pady=5)

        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
        clientes = cursor.fetchall()

        self.cliente_combobox = ttk.Combobox(
            selection_frame,
            values=[f"{c[0]} - {c[1]}" for c in clientes]
        )
        self.cliente_combobox.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        if clientes:
            self.cliente_combobox.current(0)

        # Selecionar funcionário
        ttk.Label(selection_frame, text="Funcionário:").grid(row=1, column=0, sticky="e", pady=5)

        cursor.execute("SELECT id, nome FROM funcionarios ORDER BY nome")
        funcionarios = cursor.fetchall()

        self.funcionario_combobox = ttk.Combobox(
            selection_frame,
            values=[f"{f[0]} - {f[1]}" for f in funcionarios]
        )
        self.funcionario_combobox.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        if funcionarios:
            self.funcionario_combobox.current(0)

        # Data de início e devolução
        ttk.Label(selection_frame, text="Data Início:").grid(row=2, column=0, sticky="e", pady=5)
        self.data_inicio_entry = ttk.DateEntry(selection_frame)
        self.data_inicio_entry.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
        self.data_inicio_entry.entry.delete(0, "end")
        self.data_inicio_entry.entry.insert(0, datetime.now().strftime("%m/%d/%Y"))

        ttk.Label(selection_frame, text="Data Devolução:").grid(row=3, column=0, sticky="e", pady=5)
        self.data_devolucao_entry = ttk.DateEntry(selection_frame)
        self.data_devolucao_entry.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
        self.data_devolucao_entry.entry.delete(0, "end")
        self.data_devolucao_entry.entry.insert(0, (datetime.now() + timedelta(days=7)).strftime("%m/%d/%Y"))

        # Frame de itens
        items_frame = ttk.LabelFrame(main_frame, text="Itens para Alugar", bootstyle="info")
        items_frame.pack(fill="x", pady=(0, 10))

        # Lista de itens disponíveis
        ttk.Label(items_frame, text="Item:").grid(row=0, column=0, sticky="e", pady=5)

        cursor.execute(
            "SELECT id, nome, quantidade FROM estoque WHERE status = 'disponivel' AND quantidade > 0 ORDER BY nome")
        itens_disponiveis = cursor.fetchall()

        self.item_combobox = ttk.Combobox(
            items_frame,
            values=[f"{i[0]} - {i[1]} (Disponíveis: {i[2]})" for i in itens_disponiveis]
        )
        self.item_combobox.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        if itens_disponiveis:
            self.item_combobox.current(0)

        ttk.Label(items_frame, text="Quantidade:").grid(row=0, column=2, sticky="e", pady=5, padx=5)
        self.quantidade_spinbox = ttk.Spinbox(items_frame, from_=1, to=100)
        self.quantidade_spinbox.grid(row=0, column=3, pady=5, padx=5, sticky="ew")

        add_item_btn = ttk.Button(
            items_frame,
            text="Adicionar Item",
            bootstyle="info-outline",
            command=self.add_item_to_aluguel
        )
        add_item_btn.grid(row=0, column=4, pady=5, padx=5)

        # Tabela de itens adicionados
        columns = ("id", "nome", "quantidade", "valor_diaria", "subtotal")
        self.items_tree = ttk.Treeview(
            items_frame,
            columns=columns,
            show="headings",
            height=4,
            bootstyle="dark"
        )

        self.items_tree.heading("id", text="ID")
        self.items_tree.heading("nome", text="Nome")
        self.items_tree.heading("quantidade", text="Qtd")
        self.items_tree.heading("valor_diaria", text="Valor Diária")
        self.items_tree.heading("subtotal", text="Subtotal")

        self.items_tree.column("id", width=50)
        self.items_tree.column("nome", width=150)
        self.items_tree.column("quantidade", width=50)
        self.items_tree.column("valor_diaria", width=100)
        self.items_tree.column("subtotal", width=100)

        self.items_tree.grid(row=1, column=0, columnspan=5, pady=5, sticky="ew")

        remove_item_btn = ttk.Button(
            items_frame,
            text="Remover Item",
            bootstyle="danger-outline",
            command=self.remove_item_from_aluguel
        )
        remove_item_btn.grid(row=2, column=4, pady=5, padx=5, sticky="e")

        # Frame de resumo
        summary_frame = ttk.Frame(main_frame)
        summary_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(summary_frame, text="Total de Dias:").grid(row=0, column=0, sticky="e", pady=5)
        self.total_dias_label = ttk.Label(summary_frame, text="7")
        self.total_dias_label.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        ttk.Label(summary_frame, text="Valor Total:").grid(row=1, column=0, sticky="e", pady=5)
        self.valor_total_label = ttk.Label(summary_frame, text="R$ 0.00", font=('Helvetica', 12, 'bold'))
        self.valor_total_label.grid(row=1, column=1, pady=5, padx=5, sticky="w")

        # Atualizar cálculo quando datas mudarem
        self.data_inicio_entry.entry.bind("<FocusOut>", self.calculate_total)
        self.data_devolucao_entry.entry.bind("<FocusOut>", self.calculate_total)

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)

        save_btn = ttk.Button(
            btn_frame,
            text="Salvar Aluguel",
            bootstyle="success",
            command=self.save_aluguel
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancelar",
            bootstyle="danger",
            command=self.new_window.destroy
        )
        cancel_btn.pack(side="left", padx=5)

        # Variável para armazenar itens temporários
        self.temp_items = []

    def add_item_to_aluguel(self):
        """Adiciona item à lista temporária de itens para alugar"""
        item_selecionado = self.item_combobox.get()
        quantidade = self.quantidade_spinbox.get()

        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um item!")
            return

        try:
            quantidade = int(quantidade)
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número inteiro positivo!")
            return

        item_id = int(item_selecionado.split(" - ")[0])

        # Verificar se o item já foi adicionado
        for item in self.temp_items:
            if item[0] == item_id:
                messagebox.showwarning("Aviso", "Este item já foi adicionado!")
                return

        # Obter informações do item
        cursor = self.conn.cursor()
        cursor.execute("SELECT nome, valor_diaria, quantidade FROM estoque WHERE id = ?", (item_id,))
        item_info = cursor.fetchone()

        if not item_info:
            messagebox.showerror("Erro", "Item não encontrado!")
            return

        nome, valor_diaria, disponivel = item_info

        # Verificar disponibilidade
        if quantidade > disponivel:
            messagebox.showerror("Erro", f"Quantidade indisponível! Disponível: {disponivel}")
            return

        # Adicionar à lista temporária
        self.temp_items.append((item_id, nome, quantidade, valor_diaria))

        # Atualizar tabela
        self.update_items_table()

        # Calcular total
        self.calculate_total()

    def remove_item_from_aluguel(self):
        """Remove item da lista temporária"""
        selected = self.items_tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para remover!")
            return

        item = self.items_tree.item(selected)
        item_id = item['values'][0]

        # Remover da lista temporária
        self.temp_items = [item for item in self.temp_items if item[0] != item_id]

        # Atualizar tabela
        self.update_items_table()

        # Calcular total
        self.calculate_total()

    def update_items_table(self):
        """Atualiza a tabela de itens adicionados"""
        self.items_tree.delete(*self.items_tree.get_children())
        for item in self.temp_items:
            subtotal = item[2] * item[3]  # quantidade * valor_diaria
            self.items_tree.insert("", "end", values=(
                item[0], item[1], item[2], f"R$ {item[3]:.2f}", f"R$ {subtotal:.2f}"
            ))

    def calculate_total(self, event=None):
        """Calcula o valor total do aluguel"""
        try:
            data_inicio = datetime.strptime(self.data_inicio_entry.entry.get(), "%m/%d/%Y")
            data_devolucao = datetime.strptime(self.data_devolucao_entry.entry.get(), "%m/%d/%Y")

            if data_devolucao <= data_inicio:
                messagebox.showerror("Erro", "Data de devolução deve ser após a data de início!")
                return

            dias = (data_devolucao - data_inicio).days
            self.total_dias_label.config(text=str(dias))

            total = 0.0
            for item in self.temp_items:
                subtotal = item[2] * item[3] * dias  # quantidade * valor_diaria * dias
                total += subtotal

            self.valor_total_label.config(text=f"R$ {total:.2f}")
        except ValueError:
            messagebox.showerror("Erro", "Datas inválidas! Use o formato MM/DD/AAAA")

    def save_aluguel(self):
        """Salva o novo aluguel no banco de dados"""
        if not self.temp_items:
            messagebox.showerror("Erro", "Adicione pelo menos um item ao aluguel!")
            return

        cliente_selecionado = self.cliente_combobox.get()
        funcionario_selecionado = self.funcionario_combobox.get()

        if not cliente_selecionado or not funcionario_selecionado:
            messagebox.showerror("Erro", "Selecione cliente e funcionário!")
            return

        try:
            cliente_id = int(cliente_selecionado.split(" - ")[0])
            funcionario_id = int(funcionario_selecionado.split(" - ")[0])

            data_inicio = datetime.strptime(self.data_inicio_entry.entry.get(), "%m/%d/%Y").strftime("%Y-%m-%d")
            data_devolucao = datetime.strptime(self.data_devolucao_entry.entry.get(), "%m/%d/%Y").strftime("%Y-%m-%d")

            dias = int(self.total_dias_label.cget("text"))
            valor_total = float(self.valor_total_label.cget("text").replace("R$ ", ""))

            cursor = self.conn.cursor()

            # Inserir aluguel
            cursor.execute("""
                INSERT INTO alugueis (
                    cliente_id, funcionario_id, data_inicio, data_devolucao, status, valor_total
                ) VALUES (?, ?, ?, ?, 'ativo', ?)
            """, (cliente_id, funcionario_id, data_inicio, data_devolucao, valor_total))

            aluguel_id = cursor.lastrowid

            # Inserir itens do aluguel
            for item in self.temp_items:
                cursor.execute("""
                    INSERT INTO itens_aluguel (
                        aluguel_id, item_id, quantidade, valor_unitario
                    ) VALUES (?, ?, ?, ?)
                """, (aluguel_id, item[0], item[2], item[3]))

                # Atualizar estoque
                cursor.execute("""
                    UPDATE estoque SET quantidade = quantidade - ? 
                    WHERE id = ?
                """, (item[2], item[0]))

            self.conn.commit()
            messagebox.showinfo("Sucesso", "Aluguel registrado com sucesso!")
            self.new_window.destroy()
            self.load_alugueis()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar aluguel: {str(e)}")

    def registrar_devolucao(self):
        """Registra a devolução de um aluguel ativo"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um aluguel ativo!")
            return

        item = self.tree.item(selected)
        aluguel_id = item['values'][0]
        status = item['values'][5]

        if status != 'ativo':
            messagebox.showwarning("Aviso", "Só é possível registrar devolução para aluguéis ativos!")
            return

        confirm = messagebox.askyesno(
            "Confirmar Devolução",
            f"Tem certeza que deseja registrar a devolução do aluguel #{aluguel_id}?"
        )

        if confirm:
            try:
                cursor = self.conn.cursor()

                # Atualizar status do aluguel
                cursor.execute("""
                    UPDATE alugueis SET status = 'concluido' 
                    WHERE id = ?
                """, (aluguel_id,))

                # Devolver itens ao estoque
                cursor.execute("""
                    UPDATE estoque e
                    SET quantidade = e.quantidade + ia.quantidade
                    FROM itens_aluguel ia
                    WHERE ia.aluguel_id = ? AND e.id = ia.item_id
                """, (aluguel_id,))

                self.conn.commit()
                messagebox.showinfo("Sucesso", "Devolução registrada com sucesso!")
                self.load_alugueis()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao registrar devolução: {str(e)}")

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()