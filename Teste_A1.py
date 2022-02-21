import pyodbc
import pandas as pd
import os
import numpy as np

######################### global variables ##############################
index_first_element = 1
first_element_in_query = 0
column_group_id = 'group_id'
column_material_id = 'material_id'
column_item_qty = 'item_qty'
column_item_dim_1 = 'item_dim_1'
column_item_dim_2 = 'item_dim_2'
column_item_dim_3 = 'item_dim_3'
column_item_class = 'item_class'
max_length_string_in_database = 100
password_root_database = 'lembrei'

query_to_select_data = """
    SELECT id FROM tb_dados 
    WHERE group_id = %d AND material_id = %d AND abs(item_qty-%f) <= 1e-6
"""

query_to_insert_data = """
    INSERT INTO tb_dados (group_id, material_id, item_qty, item_dim_1, item_dim_2, item_dim_3, item_class)
    VALUES (%d, %d, %f, '%s', '%s', '%s', '%s')
"""

query_to_update_data = """
    UPDATE tb_dados 
    SET group_id = %d, material_id = %d, item_qty = %f, item_dim_1 = '%s', item_dim_2 = '%s', item_dim_3 = '%s',
    item_class = '%s'
    WHERE id = %d
"""


def main(path=None):
    """
    Função principal de funcionamento do código, ela é responsável por ler um arquivo CSV em um determinado caminho,
     verificar e inserir no banco de dados
    :param path: str() caminho do arquivo, se for vazio o programa vai inserir o arquivo no diretório principal do
     projeto
    :return: list() retorna uma lista contendo todos as linhas problemáticas na hora da inserção
    """
    list_rows_problem = list()
    if not path:  # se caso não seja recebido o caminho
        actual_directory = os.getcwd()
        name_arch = 'itens.csv'
        path = actual_directory + r'/' + name_arch
    file = pd.read_csv(path, sep=';')  # abre o arquivo csv com o pandas
    file = file.replace({np.nan: 'NULL'})  # troca as linhas que estão em brancas por NULL que é o paramentro que o
    # banco de dados aceita
    for index, row in enumerate(file.iterrows()):  # percorre todas as linhas do arquivo
        if verify_data_is_valid(row[index_first_element]):
            input_data_into_database(row[index_first_element])
        else:
            list_rows_problem.append(f'line_number: {index + 1}, problematic_row: {row[index_first_element]}')
    return list_rows_problem


def verify_data_is_valid(row):
    """
    Função que verifica se a linha de forma geral é válida para a inserção no banco de dados
    :param row: set() linha do arquivo
    :return: True para dados válidos e False para dados inválidos
    """
    group_id_is_valid = verify_is_valid_number(row[column_group_id], integer=True)
    material_id_is_valid = verify_is_valid_number(row[column_material_id], integer=True)
    item_qty_is_valid = verify_is_valid_number(row[column_item_qty], integer=False)
    item_dim_1_is_valid = verify_is_valid_string(row[column_item_dim_1])
    item_dim_2_is_valid = verify_is_valid_string(row[column_item_dim_2])
    item_dim_3_is_valid = verify_is_valid_string(row[column_item_dim_3])
    item_class_is_valid = verify_is_valid_string(row[column_item_class])
    if group_id_is_valid and material_id_is_valid and item_qty_is_valid and item_dim_1_is_valid \
            and item_dim_2_is_valid and item_dim_3_is_valid and \
            item_class_is_valid:  # todas as colunas precisam ser válidas para passar nesse if
        return True
    else:
        return False


def input_data_into_database(row):
    """
    Função para inserir dados no banco, ela faz a conexão com o banco de dados, trata as linhas e insere ou
     atualiza o que está no banco
    :param row: set() linha do arquivo
    :return: None
    """
    conn = pyodbc.connect(
        "DRIVER={MySQL ODBC 3.51 Driver}; "
        "SERVER=localhost;"
        "DATABASE=banco_de_dados; "
        "PORT=3307;"
        "UID=root; "
        f"PASSWORD={password_root_database};")
    cursor = conn.cursor()  # faz a conexão com o banco
    row = transform_data_valid(row)
    # seleciona dados que já estão no banco para não forçar uma inserção de dados que já existem
    cursor.execute(query_to_select_data % (row[column_group_id], row[column_material_id], row[column_item_qty]))
    query_select = cursor.fetchone()

    if not query_select:  # se caso a seleção dos dados retornou vazia
        cursor.execute(query_to_insert_data % (row[column_group_id], row[column_material_id], row[column_item_qty],
                                               row[column_item_dim_1], row[column_item_dim_2], row[column_item_dim_3],
                                               row[column_item_class]))

    else:  # caso haja dados no banco então atualiza o que já é existente
        id_db_dados = query_select[first_element_in_query]
        cursor.execute(query_to_update_data % (row[column_group_id], row[column_material_id], row[column_item_qty],
                                               row[column_item_dim_1], row[column_item_dim_2], row[column_item_dim_3],
                                               row[column_item_class], id_db_dados))
    cursor.commit()
    cursor.close()


def verify_is_valid_number(number, integer=False):
    """
    Função para verificar se o numero recebido é realmente um número, há a verificação para inteiros e para float
    :param number: str() string em que se comparará se é um número
    :param integer: Bool() se for falso faz a verificação para float, se verdadeiro faz a verificação para inteiro
    :return: False quando não for número, True quando for número
    """
    try:
        if integer:
            int(number)
        else:
            float(str(number).replace(',', '.'))
        return True
    except ValueError:
        return False


def verify_is_valid_string(text):
    """
    Função para verificar se a string não passa o máximo do tamanho do banco
    :param text: str() texto que será verificado
    :return: True para texto que está OK, False para texto que não pode ser inserido
    """
    if len(str(text)) > max_length_string_in_database:
        return False
    else:
        return True


def transform_data_valid(row):
    """
    Função para converter a linha do arquivo para dados válidos que o banco conseguirá compreender
    :param row: set() linha do arquivo
    :return: row -> linha já tratada
    """
    row[column_group_id] = int(row[column_group_id])
    row[column_material_id] = int(row[column_material_id])
    row[column_item_qty] = float(str(row[column_item_qty]).replace(',', '.'))
    row[column_item_dim_1] = str(row[column_item_dim_1])
    row[column_item_dim_2] = str(row[column_item_dim_2])
    row[column_item_dim_3] = str(row[column_item_dim_3])
    row[column_item_class] = str(row[column_item_class])
    return row


if __name__ == '__main__':
    list_row_problems = main()
    print(list_row_problems)
