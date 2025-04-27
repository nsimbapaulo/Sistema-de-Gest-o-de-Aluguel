# database.py
import sqlite3
from sqlite3 import Error



def create_connection(db_file="gestao_aluguel.db"):
    """Cria e retorna uma conexão com o banco de dados"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        # Ativar foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Error as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def create_tables(conn):
    """Cria todas as tabelas usando a conexão fornecida"""
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        tables = [
            # Tabela de configuração do sistema
            """
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
            """,
            # Tabela de funcionários atualizada
            """
                CREATE TABLE IF NOT EXISTS funcionarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cpf TEXT UNIQUE,
                    telefone TEXT,
                    email TEXT,
                    endereco TEXT,
                    cargo TEXT,
                    salario REAL,
                    data_contratacao TEXT,
                    usuario TEXT UNIQUE,
                    senha TEXT,
                    is_admin INTEGER DEFAULT 0,
                    ativo INTEGER DEFAULT 1,
                    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """,
            # Tabela de clientes
            """
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    bi TEXT UNIQUE,
                    telefone TEXT,
                    email TEXT,
                    endereco TEXT,
                    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """,
            # Tabela de materiais/estoque
            """
                CREATE TABLE IF NOT EXISTS estoque (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    descricao TEXT,
                    quantidade INTEGER,
                    valor_diaria REAL,
                    categoria TEXT,
                    status TEXT DEFAULT 'disponivel'
                )
            """,
            # Tabela de aluguéis
            """
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
            """,
            # Tabela de itens alugados
            """
                CREATE TABLE IF NOT EXISTS itens_aluguel (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aluguel_id INTEGER,
                    item_id INTEGER,
                    quantidade INTEGER,
                    valor_unitario REAL,
                    FOREIGN KEY (aluguel_id) REFERENCES alugueis (id),
                    FOREIGN KEY (item_id) REFERENCES estoque (id)
                )
            """,
            # Tabela de pagamentos
            """
                CREATE TABLE IF NOT EXISTS pagamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aluguel_id INTEGER,
                    valor REAL,
                    data_pagamento TEXT,
                    metodo TEXT,
                    status TEXT,
                    FOREIGN KEY (aluguel_id) REFERENCES alugueis (id)
                )
            """,
            # Tabela de notificações
            """
                CREATE TABLE IF NOT EXISTS notificacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT,
                    mensagem TEXT,
                    tipo TEXT,
                    data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
                    lida INTEGER DEFAULT 0
                )
            """
   ]


        # Executa todos os comandos
        for table in tables:
            cursor.execute(table)

        conn.commit()
        return True
    except Error as e:
        print(f"Erro ao criar tabelas: {e}")
        conn.rollback()
        return False


def initialize_database():
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        conn.close()