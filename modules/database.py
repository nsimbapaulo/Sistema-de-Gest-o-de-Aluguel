import sqlite3
from sqlite3 import Error


def create_connection():
    """Cria uma conexão com o banco de dados SQLite"""
    conn = None
    try:
        conn = sqlite3.connect('gestao_aluguel.db')
        return conn
    except Error as e:
        print(e)

    return conn


def create_tables(conn):
    """Cria todas as tabelas necessárias"""
    try:
        cursor = conn.cursor()

        # Tabela de clientes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            bi TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Tabela de funcionários
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            bi TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            cargo TEXT,
            salario REAL,
            data_contratacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Tabela de materiais/estoque
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            quantidade INTEGER,
            valor_diaria REAL,
            categoria TEXT,
            status TEXT DEFAULT 'disponivel'
        )
        """)

        # Tabela de aluguéis
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alugueis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            funcionario_id INTEGER,
            data_inicio TEXT,
            data_devolucao TEXT,
            status TEXT DEFAULT 'ativo',
            valor_total REAL,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id),
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios (id)
        )
        """)

        # Tabela de itens alugados
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_aluguel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluguel_id INTEGER,
            item_id INTEGER,
            quantidade INTEGER,
            valor_unitario REAL,
            FOREIGN KEY (aluguel_id) REFERENCES alugueis (id),
            FOREIGN KEY (item_id) REFERENCES estoque (id)
        )
        """)

        # Tabela de pagamentos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluguel_id INTEGER,
            valor REAL,
            data_pagamento TEXT,
            metodo TEXT,
            status TEXT,
            FOREIGN KEY (aluguel_id) REFERENCES alugueis (id)
        )
        """)

        # Tabela de notificações
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notificacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            mensagem TEXT,
            tipo TEXT,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
            lida INTEGER DEFAULT 0
        )
        """)

        conn.commit()
    except Error as e:
        print(e)


def initialize_database():
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        conn.close()