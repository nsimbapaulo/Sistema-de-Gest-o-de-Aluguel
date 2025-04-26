import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from .database import create_connection


class EstoqueModule:
    def __init__(self, parent):
        self.parent = parent
        self.conn = create_connection()
        self.create_widgets()
        self.load_estoque()

    def create_widgets(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame de busca
        search_frame = ttk.LabelFrame(self.main_frame, text="Buscar Item", bootstyle="info")
        search_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(search_frame, text="Nome/Categoria:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)

        search_btn = ttk.Button(
            search_frame,
            text="Buscar",
            bootstyle="info-outline",
            command=self.search_item
        )
        search_btn.pack(side="left", padx=5)

        # Frame de ações
        actions_frame = ttk.Frame(self.main_frame)
        actions_frame.pack(fill="x", pady=(0, 10))

        add_btn = ttk.Button(
            actions_frame,
            text="Adicionar Item",
            bootstyle="success",
            command=self.open_add_item
        )
        add_btn.pack(side="left", padx=5)

        edit_btn = ttk.Button(
            actions_frame,
            text="Editar",
            bootstyle="warning",
            command=self.open_edit_item
        )
        edit_btn.pack(side="left", padx=5)

        remove_btn = ttk.Button(
            actions_frame,
            text="Remover",
            bootstyle="danger",
            command=self.remove_item
        )
        remove_btn.pack(side="left", padx=5)

        # Tabela de estoque
        columns = ("id", "nome", "descricao", "quantidade", "valor_diaria", "categoria", "status")
        self.tree = ttk.Treeview(
            self.main_frame,
            columns=columns,
            show="headings",
            bootstyle="dark"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("descricao", text="Descrição")
        self.tree.heading("quantidade", text="Quantidade")
        self.tree.heading("valor_diaria", text="Valor Diária")
        self.tree.heading("categoria", text="Categoria")
        self.tree.heading("status", text="Status")

        self.tree.column("id", width=50)
        self.tree.column("nome", width=150)
        self.tree.column("descricao", width=200)
        self.tree.column("quantidade", width=80)
        self.tree.column("valor_diaria", width=100)
        self.tree.column("categoria", width=120)
        self.tree.column("status", width=100)

        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configurar tags para status
        self.tree.tag_configure('disponivel', background='#e6ffe6')
        self.tree.tag_configure('indisponivel', background='#ffe6e6')

    def load_estoque(self):
        """Carrega todos os itens na tabela"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome, descricao, quantidade, valor_diaria, categoria, status FROM estoque")
        rows = cursor.fetchall()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            tags = (row[6].lower(),)  # Usa o status como tag
            self.tree.insert("", "end", values=row, tags=tags)

    def search_item(self):
        """Busca itens por nome ou categoria"""
        search_term = self.search_entry.get()
        cursor = self.conn.cursor()

        if search_term:
            cursor.execute(
                "SELECT id, nome, descricao, quantidade, valor_diaria, categoria, status FROM estoque "
                "WHERE nome LIKE ? OR categoria LIKE ?",
                (f"%{search_term}%", f"%{search_term}%")
            )
        else:
            cursor.execute("SELECT id, nome, descricao, quantidade, valor_diaria, categoria, status FROM estoque")

        rows = cursor.fetchall()
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            tags = (row[6].lower(),)
            self.tree.insert("", "end", values=row, tags=tags)

    def open_add_item(self):
        """Abre janela para adicionar novo item"""
        self.add_window = ttk.Toplevel(self.parent)
        self.add_window.title("Adicionar Item ao Estoque")

        # Formulário
        form_frame = ttk.Frame(self.add_window)
        form_frame.pack(padx=10, pady=10)

        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky="e", pady=5)
        self.nome_entry = ttk.Entry(form_frame)
        self.nome_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Descrição:").grid(row=1, column=0, sticky="e", pady=5)
        self.descricao_entry = ttk.Entry(form_frame)
        self.descricao_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Quantidade:").grid(row=2, column=0, sticky="e", pady=5)
        self.quantidade_entry = ttk.Spinbox(form_frame, from_=0, to=999)
        self.quantidade_entry.grid(row=2, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Valor Diária:").grid(row=3, column=0, sticky="e", pady=5)
        self.valor_entry = ttk.Entry(form_frame)
        self.valor_entry.grid(row=3, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Categoria:").grid(row=4, column=0, sticky="e", pady=5)
        self.categoria_combobox = ttk.Combobox(
            form_frame,
            values=["Ferramenta", "Equipamento", "Veículo", "Eletrônico", "Outros"]
        )
        self.categoria_combobox.grid(row=4, column=1, pady=5, padx=5)
        self.categoria_combobox.current(0)

        ttk.Label(form_frame, text="Status:").grid(row=5, column=0, sticky="e", pady=5)
        self.status_combobox = ttk.Combobox(
            form_frame,
            values=["disponivel", "indisponivel", "manutencao"]
        )
        self.status_combobox.grid(row=5, column=1, pady=5, padx=5)
        self.status_combobox.current(0)

        # Botões
        btn_frame = ttk.Frame(self.add_window)
        btn_frame.pack(pady=10)

        save_btn = ttk.Button(
            btn_frame,
            text="Salvar",
            bootstyle="success",
            command=self.save_item
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancelar",
            bootstyle="danger",
            command=self.add_window.destroy
        )
        cancel_btn.pack(side="left", padx=5)

    def save_item(self):
        """Salva novo item no banco de dados"""
        nome = self.nome_entry.get()
        descricao = self.descricao_entry.get()
        quantidade = self.quantidade_entry.get()
        valor_diaria = self.valor_entry.get()
        categoria = self.categoria_combobox.get()
        status = self.status_combobox.get()

        if not nome:
            messagebox.showerror("Erro", "O nome é obrigatório!")
            return

        try:
            quantidade = int(quantidade)
            valor_diaria = float(valor_diaria)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e valor devem ser números válidos!")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO estoque (nome, descricao, quantidade, valor_diaria, categoria, status) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (nome, descricao, quantidade, valor_diaria, categoria, status)
            )
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Item cadastrado com sucesso!")
            self.add_window.destroy()
            self.load_estoque()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar item: {str(e)}")

    def open_edit_item(self):
        """Abre janela para editar item selecionado"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para editar!")
            return

        item = self.tree.item(selected)
        item_id = item['values'][0]

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM estoque WHERE id = ?", (item_id,))
        item_data = cursor.fetchone()

        self.edit_window = ttk.Toplevel(self.parent)
        self.edit_window.title("Editar Item")
        self.current_item_id = item_id

        # Formulário
        form_frame = ttk.Frame(self.edit_window)
        form_frame.pack(padx=10, pady=10)

        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky="e", pady=5)
        self.edit_nome_entry = ttk.Entry(form_frame)
        self.edit_nome_entry.grid(row=0, column=1, pady=5, padx=5)
        self.edit_nome_entry.insert(0, item_data[1])

        ttk.Label(form_frame, text="Descrição:").grid(row=1, column=0, sticky="e", pady=5)
        self.edit_descricao_entry = ttk.Entry(form_frame)
        self.edit_descricao_entry.grid(row=1, column=1, pady=5, padx=5)
        self.edit_descricao_entry.insert(0, item_data[2])

        ttk.Label(form_frame, text="Quantidade:").grid(row=2, column=0, sticky="e", pady=5)
        self.edit_quantidade_entry = ttk.Spinbox(form_frame, from_=0, to=999)
        self.edit_quantidade_entry.grid(row=2, column=1, pady=5, padx=5)
        self.edit_quantidade_entry.set(item_data[3])

        ttk.Label(form_frame, text="Valor Diária:").grid(row=3, column=0, sticky="e", pady=5)
        self.edit_valor_entry = ttk.Entry(form_frame)
        self.edit_valor_entry.grid(row=3, column=1, pady=5, padx=5)
        self.edit_valor_entry.insert(0, item_data[4])

        ttk.Label(form_frame, text="Categoria:").grid(row=4, column=0, sticky="e", pady=5)
        self.edit_categoria_combobox = ttk.Combobox(
            form_frame,
            values=["Ferramenta", "Equipamento", "Veículo", "Eletrônico", "Outros"]
        )
        self.edit_categoria_combobox.grid(row=4, column=1, pady=5, padx=5)
        self.edit_categoria_combobox.set(item_data[5])

        ttk.Label(form_frame, text="Status:").grid(row=5, column=0, sticky="e", pady=5)
        self.edit_status_combobox = ttk.Combobox(
            form_frame,
            values=["disponivel", "indisponivel", "manutencao"]
        )
        self.edit_status_combobox.grid(row=5, column=1, pady=5, padx=5)
        self.edit_status_combobox.set(item_data[6])

        # Botões
        btn_frame = ttk.Frame(self.edit_window)
        btn_frame.pack(pady=10)

        save_btn = ttk.Button(
            btn_frame,
            text="Salvar Alterações",
            bootstyle="success",
            command=self.update_item
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancelar",
            bootstyle="danger",
            command=self.edit_window.destroy
        )
        cancel_btn.pack(side="left", padx=5)

    def update_item(self):
        """Atualiza item no banco de dados"""
        nome = self.edit_nome_entry.get()
        descricao = self.edit_descricao_entry.get()
        quantidade = self.edit_quantidade_entry.get()
        valor_diaria = self.edit_valor_entry.get()
        categoria = self.edit_categoria_combobox.get()
        status = self.edit_status_combobox.get()

        if not nome:
            messagebox.showerror("Erro", "O nome é obrigatório!")
            return

        try:
            quantidade = int(quantidade)
            valor_diaria = float(valor_diaria)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e valor devem ser números válidos!")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE estoque SET nome = ?, descricao = ?, quantidade = ?, "
                "valor_diaria = ?, categoria = ?, status = ? WHERE id = ?",
                (nome, descricao, quantidade, valor_diaria, categoria, status, self.current_item_id)
            )
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Item atualizado com sucesso!")
            self.edit_window.destroy()
            self.load_estoque()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar item: {str(e)}")

    def remove_item(self):
        """Remove item selecionado"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para remover!")
            return

        item = self.tree.item(selected)
        item_id = item['values'][0]
        item_nome = item['values'][1]

        # Verificar se o item está em algum aluguel ativo
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM itens_aluguel ia
            JOIN alugueis a ON ia.aluguel_id = a.id
            WHERE ia.item_id = ? AND a.status = 'ativo'
        """, (item_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            messagebox.showerror("Erro", "Este item está em um aluguel ativo e não pode ser removido!")
            return

        confirm = messagebox.askyesno(
            "Confirmar",
            f"Tem certeza que deseja remover o item {item_nome}?"
        )

        if confirm:
            try:
                cursor.execute("DELETE FROM estoque WHERE id = ?", (item_id,))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Item removido com sucesso!")
                self.load_estoque()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover item: {str(e)}")

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()