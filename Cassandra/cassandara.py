from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
import uuid
from datetime import datetime

cloud_config = {
    'secure_connect_bundle': 'secure-connect-cassandra.zip'
}
auth_provider = PlainTextAuthProvider('ZqZpXrXBADhOWsWShRUilpLX', 'R2o8DYJc9mgKF6pn.GHE_6QOUxkj6NwMN2X,T9a3a43OKwqZkJ0ZZAwHL3ZEMYktlQ4Zc6ZS01JZaXC4kfhPZrZ.mLJCODRcjYZ.S.+oc8KYl9ZF97o1E9G-.LrT-6N6')
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()
KEYSPACE = 'default_keyspace'

session.execute(f"USE {KEYSPACE}")

def criarTabelas():
    create_table_fornecedor = f"""
    CREATE TABLE IF NOT EXISTS {KEYSPACE}.fornecedor (
        id UUID PRIMARY KEY,
        nome TEXT,
        email TEXT,
        senha TEXT,
        endereco MAP<TEXT, TEXT>,
        telefone MAP<TEXT, TEXT>,
        data_criacao TIMESTAMP
    );
    """
    create_table_usuario = f"""
    CREATE TABLE IF NOT EXISTS {KEYSPACE}.usuario (
        id UUID PRIMARY KEY,
        nome TEXT,
        email TEXT,
        senha TEXT,
        endereco MAP<TEXT, TEXT>,
        telefone MAP<TEXT, TEXT>,
        data_criacao TIMESTAMP
    );
    """
    create_table_produto = f"""
    CREATE TABLE IF NOT EXISTS {KEYSPACE}.produto (
        id UUID PRIMARY KEY,
        nome TEXT,
        quantidade INT,
        descricao TEXT,
        preco DOUBLE,
        marca TEXT,
        categoria TEXT,
        imagem TEXT,
        data_criacao TIMESTAMP,
        fornecedor_id UUID
    );
    """
    create_table_compras = f"""
    CREATE TABLE IF NOT EXISTS {KEYSPACE}.compras (
        id UUID PRIMARY KEY,
        usuario_id UUID,
        produtos LIST<FROZEN<MAP<TEXT, TEXT>>>,
        valor_total DOUBLE,
        forma_pagamento TEXT,
        data_pagamento TIMESTAMP
    );
    """

    session.execute(create_table_fornecedor)
    session.execute(create_table_usuario)
    session.execute(create_table_produto)
    session.execute(create_table_compras)


def insertFornecedor():
    fornecedor_id = uuid.uuid4()
    nome = input("Nome: ")
    email = input("Email: ")
    senha = input("Senha: ")
    endereco = {
        "logradouro": input("Logradouro: "),
        "numero": input("Numero: "),
        "complemento": input("Complemento: "),
        "bairro": input("Bairro: "),
        "cidade": input("Cidade: "),
        "estado": input("Estado: "),
        "cep": input("CEP: ")
    }
    tipo = input("Escolha o tipo de telefone entre Celular ou Residencial: ").upper()
    numero = input("Número de telefone: ")
    telefone = {"tipo": tipo, "numero": numero}
    data_criacao = datetime.now()

    query = f"""
    INSERT INTO {KEYSPACE}.fornecedor (id, nome, email, senha, endereco, telefone, data_criacao)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    session.execute(query, (fornecedor_id, nome, email, senha, endereco, telefone, data_criacao))
    print("Fornecedor inserido com sucesso.")

def insertUsuario():
    usuario_id = uuid.uuid4()
    nome = input("Nome: ")
    email = input("Email: ")
    senha = input("Senha: ")
    endereco = {
        "logradouro": input("Logradouro: "),
        "numero": input("Numero: "),
        "complemento": input("Complemento: "),
        "bairro": input("Bairro: "),
        "cidade": input("Cidade: "),
        "estado": input("Estado: "),
        "cep": input("CEP: ")
    }
    tipo = input("Escolha o tipo de telefone entre Celular ou Residencial: ").upper()
    numero = input("Número de telefone: ")
    telefone = {"tipo": tipo, "numero": numero}
    data_criacao = datetime.now()

    query = f"""
    INSERT INTO {KEYSPACE}.usuario (id, nome, email, senha, endereco, telefone, data_criacao)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    session.execute(query, (usuario_id, nome, email, senha, endereco, telefone, data_criacao))
    print("Usuário inserido com sucesso.")


def insertProduto():
    produto_id = uuid.uuid4()
    nome = input("Nome: ")
    quantidade = int(input("Quantidade: "))
    descricao = input("Descrição: ")
    preco = float(input("Preço: "))
    marca = input("Marca: ")
    categoria = input("Categoria: ")
    imagem = input("Imagem: ")
    fornecedor_id = input("ID do Fornecedor: ")
    data_criacao = datetime.now()

    query = f"""
    INSERT INTO {KEYSPACE}.produto (id, nome, quantidade, descricao, preco, marca, categoria, imagem, data_criacao, fornecedor_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    session.execute(query, (produto_id, nome, quantidade, descricao, preco, marca, categoria, imagem, data_criacao, uuid.UUID(fornecedor_id)))
    print("Produto inserido com sucesso")


def realizarCompra():
    print("Realizando Compra\n")
    
    id_usuario = input("ID do Usuário: ")
    usuario_existente = session.execute(f"SELECT * FROM {KEYSPACE}.usuario WHERE id = %s", [uuid.UUID(id_usuario)]).one()
    if not usuario_existente:
        print(f"Usuário com ID {id_usuario} não encontrado.")
        print("Por favor, verifique o ID do usuário e tente novamente.")
        return
    
    produtos_compra = []
    valor_total = 0
    
    while True:
        id_produto = input("ID do Produto: ")
        produto_existente = session.execute(f"SELECT * FROM {KEYSPACE}.produto WHERE id = %s", [uuid.UUID(id_produto)]).one()
        if not produto_existente:
            print(f"Produto com ID {id_produto} não encontrado.")
            print("Por favor, verifique o ID do produto e tente novamente.")
            continue
        
        try:
            quantidade = int(input("Quantidade do Produto: "))
            if quantidade <= 0:
                print("Quantidade inválida. A quantidade deve ser maior que zero.")
                continue
        except ValueError:
            print("Quantidade inválida. Insira um valor numérico.")
            continue
        
        valor_produto = produto_existente.preco * quantidade
        valor_total += valor_produto
        
        produtos_compra.append({
            "produto_id": str(produto_existente.id),
            "fornecedor_id": str(produto_existente.fornecedor_id),
            "quantidade": str(quantidade),
            "valor_produto": str(valor_produto)
        })
        
        continuar = input("Deseja adicionar mais produtos? (S/N): ").strip().lower()
        if continuar != 's':
            break
    
    if not produtos_compra:
        print("Nenhum produto selecionado. A compra não pode ser realizada.")
        return
    
    forma_pagamento = input("Forma de pagamento (PIX ou Cartão de Crédito): ").lower()
    while forma_pagamento not in ["pix", "cartão de crédito"]:
        print("Forma de pagamento inválida. Escolha entre PIX ou Cartão de Crédito.")
        forma_pagamento = input("Forma de pagamento (PIX ou Cartão de Crédito): ").lower()
    
    data_pagamento = datetime.now()
    
    compra_id = uuid.uuid4()
    
    session.execute(
        f"""
        INSERT INTO {KEYSPACE}.compras (id, usuario_id, produtos, valor_total, forma_pagamento, data_pagamento)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (compra_id, uuid.UUID(id_usuario), produtos_compra, valor_total, forma_pagamento, data_pagamento)
    )
    
    print("Compra realizada com sucesso.")










def listarFornecedores():
    query = f"SELECT * FROM {KEYSPACE}.fornecedor"
    result = session.execute(query)
    print("Lista de Fornecedores:")
    for linha in result:
        print(f"ID: {linha.id}")
        print(f"Nome: {linha.nome}")
        print(f"Email: {linha.email}")
        endereco = linha.endereco
        print("Endereço:")
        print(f"  Logradouro: {endereco['logradouro']}")
        print(f"  Número: {endereco['numero']}")
        print(f"  Complemento: {endereco['complemento']}")
        print(f"  Bairro: {endereco['bairro']}")
        print(f"  Cidade: {endereco['cidade']}")
        print(f"  Estado: {endereco['estado']}")
        print(f"  CEP: {endereco['cep']}")
        telefone = linha.telefone
        print("Telefone:")
        print(f"  Tipo: {telefone.get('tipo')}")
        print(f"  Número: {telefone.get('numero')}")
        print(f"Data de Criação: {linha.data_criacao}")
        print()

def listarUsuarios():
    query = f"SELECT * FROM {KEYSPACE}.usuario"
    result = session.execute(query)
    print("Lista de Usuários:")
    for linha in result:
        print(f"ID: {linha.id}")
        print(f"Nome: {linha.nome}")
        print(f"Email: {linha.email}")
        endereco = linha.endereco
        print("Endereço:")
        print(f"  Logradouro: {endereco['logradouro']}")
        print(f"  Número: {endereco['numero']}")
        print(f"  Complemento: {endereco['complemento']}")
        print(f"  Bairro: {endereco['bairro']}")
        print(f"  Cidade: {endereco['cidade']}")
        print(f"  Estado: {endereco['estado']}")
        print(f"  CEP: {endereco['cep']}")
        telefone = linha.telefone
        print("Telefone:")
        print(f"  Tipo: {telefone.get('tipo')}")
        print(f"  Número: {telefone.get('numero')}")
        print(f"Data de Criação: {linha.data_criacao}")
        print()

def listarProdutos():
    query = f"SELECT * FROM {KEYSPACE}.produto"
    result = session.execute(query)
    print("Lista de Produtos")
    for linha in result:
        print(f"ID: {linha.id}")
        print(f"Nome: {linha.nome}")
        print(f"Quantidade: {linha.quantidade}")
        print(f"Descrição: {linha.descricao}")
        print(f"Preço: {linha.preco}")
        print(f"Marca: {linha.marca}")
        print(f"Categoria: {linha.categoria}")
        print(f"Imagem: {linha.imagem}")
        print(f"Data Criação: {linha.data_criacao}")
        print()
    
def listarCompras():
    query = f"SELECT * FROM {KEYSPACE}.compras"
    result = session.execute(query)
    print("Lista de Compras:")
    for row in result:
        print(f"ID: {row.id}")
        print(f"ID do Usuário: {row.usuario_id}")
        print("Produtos:")
        for produto in row.produtos:
            print(f"  Produto ID: {produto['produto_id']}")
            print(f"  Fornecedor ID: {produto['fornecedor_id']}")
            print(f"  Quantidade: {produto['quantidade']}")
            print(f"  Valor do Produto: {produto['valor_produto']}")
        print(f"Valor Total: {row.valor_total}")
        print(f"Forma de Pagamento: {row.forma_pagamento}")
        print(f"Data de Pagamento: {row.data_pagamento}")
        print()










def updateUsuario():
    id_usuario = input("Digite o ID do usuário que deseja atualizar: ")
    usuario_existente = session.execute(f"SELECT * FROM {KEYSPACE}.usuario WHERE id = %s", [uuid.UUID(id_usuario)]).one()
    
    if not usuario_existente:
        print(f"Usuário com ID {id_usuario} não encontrado.")
        print("Por favor, verifique o ID do usuário e tente novamente.")
        return
    
    print("Usuário encontrado. Por favor, insira as novas informações.")
    
    nome = usuario_existente.nome
    email = usuario_existente.email
    senha = usuario_existente.senha
    endereco_atualizado = usuario_existente.endereco
    telefone_atualizado = usuario_existente.telefone

    print("\nAtualizando informações do usuário\n")
    while True:
        pergunta = input("Deseja atualizar seus dados? (S/N) ").upper()
        while pergunta not in ["S", "N", "SIM", "NAO", "NÃO"]:
            print("Resposta inválida. Tente novamente.")
            pergunta = input("Deseja atualizar seus dados? (S/N) ").upper()
        if pergunta in ["S", "SIM"]:
            nome = input("Nome: ")
            email = input("Email: ")
            senha = input("Senha: ")
            break
        elif pergunta in ["N", "NAO", "NÃO"]:
            break

    while True:
        resposta = input("Deseja Atualizar Endereço? (S/N) ").upper()
        while resposta not in ["S", "N", "SIM", "NAO", "NÃO"]:
            print("Resposta inválida. Tente novamente.")
            resposta = input("Deseja Atualizar Endereço? (S/N) ").upper()
        if resposta in ["S", "SIM"]:
            endereco_atualizado = {
                "logradouro": input("Logradouro: "),
                "numero": input("Numero: "),
                "complemento": input("Complemento: "),
                "bairro": input("Bairro: "),
                "cidade": input("Cidade: "),
                "estado": input("Estado: "),
                "cep": input("CEP: ")
            }
            break
        elif resposta in ["N", "NAO", "NÃO"]:
            break

    while True:
        resposta = input("Deseja Atualizar Telefone? (S/N) ").upper()
        while resposta not in ["S", "N", "SIM", "NAO", "NÃO"]:
            print("Resposta inválida. Tente novamente.")
            resposta = input("Deseja Atualizar Telefone? (S/N) ").upper()
        if resposta in ["S", "SIM"]:
            tipo = input("Escolha o tipo de telefone entre Celular ou Residencial: ").upper()
            while tipo not in ["CELULAR", "RESIDENCIAL"]:
                print("Tipo de telefone inválido. Tente novamente.")
                tipo = input("Escolha o tipo de telefone entre Celular ou Residencial: ").upper()
            numero = input("Número de telefone: ")
            telefone_atualizado.append({"tipo": tipo, "numero": numero})
            break
        elif resposta in ["N", "NAO", "NÃO"]:
            break

    while True:
        resposta_endereco = input("Deseja adicionar mais um endereço? (S/N) ").upper()
        while resposta_endereco not in ["S", "N", "SIM", "NAO", "NÃO"]:
            print("Resposta inválida. Tente novamente.")
            resposta_endereco = input("Deseja adicionar mais um endereço? (S/N) ").upper()
        if resposta_endereco in ["S", "SIM"]:
            novo_endereco = {
                "logradouro": input("Logradouro: "),
                "numero": input("Numero: "),
                "complemento": input("Complemento: "),
                "bairro": input("Bairro: "),
                "cidade": input("Cidade: "),
                "estado": input("Estado: "),
                "cep": input("CEP: ")
            }
            endereco_atualizado.append(novo_endereco)
        elif resposta_endereco in ["N", "NAO", "NÃO"]:
            break

    while True:
        resposta_telefone = input("Deseja adicionar mais um telefone? (S/N) ").upper()
        while resposta_telefone not in ["S", "N", "SIM", "NAO", "NÃO"]:
            print("Resposta inválida. Tente novamente.")
            resposta_telefone = input("Deseja adicionar mais um telefone? (S/N) ").upper()
        if resposta_telefone in ["S", "SIM"]:
            tipo = input("Escolha o tipo de telefone entre Celular ou Residencial: ").upper()
            while tipo not in ["CELULAR", "RESIDENCIAL"]:
                print("Tipo de telefone inválido. Tente novamente.")
                tipo = input("Escolha o tipo de telefone entre Celular ou Residencial: ").upper()
            numero = input("Número de telefone: ")
            telefone_atualizado.append({"tipo": tipo, "numero": numero})
            break
        elif resposta_telefone in ["N", "NAO", "NÃO"]:
            break

    session.execute(
        f"""
        UPDATE {KEYSPACE}.usuario
        SET nome = %s, email = %s, senha = %s, endereco = %s, telefone = %s
        WHERE id = %s
        """,
        (nome, email, senha, endereco_atualizado, telefone_atualizado, uuid.UUID(id_usuario))
    )
    print("Usuário atualizado com sucesso")

def deleteCompra():
    id_compra = input("Digite o ID da compra que deseja deletar: ")
    compra_existente = session.execute(f"SELECT * FROM {KEYSPACE}.compras WHERE id = %s", [uuid.UUID(id_compra)]).one()

    if not compra_existente:
        print(f"Compra com ID {id_compra} não encontrada.")
        print("Por favor, verifique o ID da compra e tente novamente.")
        return

    session.execute(f"DELETE FROM {KEYSPACE}.compras WHERE id = %s", [uuid.UUID(id_compra)])
    print("Compra deletada com sucesso.")


def menu():
    loop = True
    while loop:
        print("""
            1 - Insert Usuario\n
            2 - Insert Fornecedor\n
            3 - Insert Produto\n
            4 - Realizar Compra\n
            5 - Listar Usuario\n
            6 - Listar Fornecedor\n
            7 - Listar Produto\n
            8 - Listar Compras\n
            9 - Atualizar Usuario\n
            10 - Deletar Compra\n
            11 - Criar Tabelas\n
            0 - Sair
        """)
        escolha = input("Digite a Operação desejada: ")
        match escolha:
            case "1":
                insertUsuario()
            case "2":
                insertFornecedor()
            case "3":
                insertProduto()
            case "4":
                realizarCompra()
            case "5":
                listarUsuarios()
            case "6":
                listarFornecedores()
            case "7":
                listarProdutos()
            case "8":
                listarCompras()
            case "9":
                updateUsuario()
            case "10":
                deleteCompra()
            case "11":
                criarTabelas()
            case "0":
                print("Saindo...")
                loop = False

menu()