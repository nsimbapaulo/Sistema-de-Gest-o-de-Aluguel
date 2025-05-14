from .database import initialize_database, create_connection


def execute(query, params=None, commit:bool=False):
    conn =  create_connection()
    c = conn.cursor()

    c.execute(query, params) if params else  c.execute(query)
    r = c.fetchall()

    if commit:
        conn.commit()
    conn.close()
    return r

def view_table(table:str, columns:str=None)-> list[list[str]]:
    """

    :param table: tabela que deseja visualizar
    :param columns: selecionar colunas a ver
    :return: retorna os dados da tabela
    """
    if not columns:
        query = f"""SELECT * FROM {table}"""
    else:
        query = f"""SELECT {columns} FROM {table}"""
    return execute(query)

def insert_data(table:str, *args):
    """

    :param table: tabelas que deseja inserir os dados
    :param args: os dados a serem inseridos
    :return: retorna (True, None) se os dados foram inseridos, senão (False, mess_error)

    As tabelas são pre-definidas: config, funcionarios, clientes, estoque,
    alugueis, itens_aluguel, pagamentos.
    """
    table_dic = {
        "config": ["""INSERT INTO config ( company_name, company_cnpj, company_phone, company_email,
                                        company_address, company_logo, theme, currency,
                                        backup_dir, reports_dir, setup_complete )
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""", args],

        "funcionarios": ["""INSERT INTO funcionarios( nome, bi, telefone, email, endereco, cargo, salario,
                                                    data_contratacao, usuario, senha, is_admin, ativo )
                                                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", args],

        "clientes": ["""INSERT INTO clientes (nome, bi, telefone, email, endereco) 
                        VALUES (?, ?, ?, ?, ?)""", args],

        "estoque": ["""INSERT INTO estoque (nome, descricao, quantidade, valor_diaria, categoria, status) 
                            VALUES (?, ?, ?, ?, ?, ?)""", args],

        "alugueis": ["""INSERT INTO alugueis (
                            cliente_id, funcionario_id, data_inicio, data_devolucao, status, valor_total )
                        VALUES (?, ?, ?, ?, 'ativo', ?)""", args],

        "itens_aluguel": ["""INSERT INTO itens_aluguel ( aluguel_id, item_id, quantidade, valor_unitario )
                             VALUES (?, ?, ?, ?)""", args],

        "pagamentos": [""""INSERT INTO pagamentos(aluguel_id, valor, data_pagamento, metodo, status )
                             VALUES(?, ?, datetime('now'), ?, 'pago')""", args],
    }

    try:
        execute(table_dic[table][0], table_dic[table][1], commit=False)
        return True, None
    except Exception as e:
        mess_error = str(e)
        return False, mess_error

def update_data(table:str, set_col, valuer:str, refer_col:str, refer_table:str=None, *ref_valuer):
    query = """
                UPDATE estoque e
                SET quantidade = e.quantidade + ia.quantidade
                FROM itens_aluguel ia
                WHERE ia.aluguel_id = ? AND e.id = ia.item_id
            """

def find_data(table: str, return_col: str, find_in_col: str, search_term: str) -> list[list[str]]:
    """
        :param table: tabela a buscar
        :param return_col: coluna a ser retornada
        :param find_in_col: coluna a buscar
        :param search_term: valor a pesquisar
        :return: retornar dados das colunas.
    """
    colunas = [col.strip() for col in find_in_col.split(',') if col.strip()]
    if not colunas:
        raise ValueError("Nenhuma coluna válida fornecida para busca.")

    # Monta cláusula WHERE com LIKEs encadeados por OR
    where_clause = ' OR '.join([f"{col} LIKE ?" for col in colunas])

    query = f"""
                SELECT {return_col}
                FROM {table}
                WHERE {where_clause}
             """
    # Um parâmetro LIKE para cada coluna
    params = tuple(f"%{search_term}%" for _ in colunas)

    return execute(query, params)

def delete_column():
    ...


# config --------------> Tabela de configuração do sistema
# funcionarios --------> Tabela de funcionários atualizada
# clientes ------------> Tabela de clientes
# estoque -------------> Tabela de materiais/estoque
# alugueis ------------> Tabela de aluguéis
# itens_aluguel -------> Tabela de itens alugados
# pagamentos ----------> Tabela de pagamentos
