import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure
import os
import hashlib 
from datetime import datetime

uri = "mongodb+srv://lucasguerra:lucasguerra@projetoloja.11g2zmw.mongodb.net/"

def conectar_db():
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("✅ Conexão com o MongoDB Atlas estabelecida com sucesso!")
        db = client["mercadolivre"] 
        
        usuarios = db["usuarios"]
        vendedores = db["vendedores"]
        
        return usuarios, vendedores
    except ConnectionFailure as e:
        print(f"❌ Não foi possível conectar ao MongoDB Atlas. Erro: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")
        return None, None

# FUNÇÕES CRUD PARA USUÁRIOS E FAVORITOS

def criar_usuario(colecao_usuarios):
    print("\n--- 👤 Adicionar Novo Usuário ---")
    nome = input("Nome: ")
    sobrenome = input("Sobrenome: ")
    cpf = input("CPF (apenas números): ")
    email = input("E-mail: ")
    senha_plana = input("Senha: ")
    senha_hash = hashlib.sha256(senha_plana.encode()).hexdigest()
    
    novo_usuario = {
        "id_usuario": f"U{colecao_usuarios.count_documents({}) + 1}",
        "nome": nome, "sobrenome": sobrenome, "cpf": cpf, "email": email,
        "senha": senha_hash, "favoritos": [], "compras": []
    }
    colecao_usuarios.insert_one(novo_usuario)
    print(f"\n✅ Usuário '{nome} {sobrenome}' inserido com sucesso!")

def ler_usuarios(colecao_usuarios):
    print("\n--- 📋 Lista de Usuários ---")
    if colecao_usuarios.count_documents({}) == 0:
        print("Nenhum usuário encontrado."); return
    for usuario in colecao_usuarios.find().sort("nome"):
        print(f"\n👤 ID: {usuario.get('id_usuario')} | Nome: {usuario.get('nome')} {usuario.get('sobrenome')} | CPF: {usuario.get('cpf')}")
        if usuario.get('favoritos'):
            print(f"   ⭐ Favoritos: {len(usuario.get('favoritos'))} item(s)")
        if usuario.get('compras'):
            print(f"   🛒 Compras: {len(usuario.get('compras'))} item(s)")

# FUNÇÃO PARA FAVORITOS
def gerenciar_favoritos(colecao_usuarios, colecao_vendedores):
    print("\n--- ⭐ Gerenciar Favoritos ---")
    cpf_usuario = input("Digite o CPF do usuário para gerenciar os favoritos: ")
    usuario = colecao_usuarios.find_one({"cpf": cpf_usuario})
    if not usuario:
        print("❌ Usuário não encontrado."); return
    
    print(f"Gerenciando favoritos de {usuario.get('nome')}.")
    print("1 - Adicionar Produto aos Favoritos")
    print("2 - Remover Produto dos Favoritos")
    escolha = input("Opção: ")

    if escolha == '1':
        # Listar todos os produtos de todos os vendedores
        produtos_disponiveis = []
        for vendedor in colecao_vendedores.find():
            for produto in vendedor.get("produtos", []):
                produtos_disponiveis.append(produto)
        
        if not produtos_disponiveis:
            print("Não há produtos no sistema para adicionar aos favoritos."); return

        print("\n--- Produtos Disponíveis ---")
        for i, produto in enumerate(produtos_disponiveis):
            print(f"{i + 1} - {produto['nome']} (ID: {produto['id_produto']})")
        
        try:
            escolha_prod = int(input("Escolha o número do produto para favoritar: ")) - 1
            produto_escolhido = produtos_disponiveis[escolha_prod]
        except (ValueError, IndexError):
            print("❌ Escolha inválida."); return

        novo_favorito = {
            "id_produto": produto_escolhido['id_produto'],
            "data_adicao": datetime.now()
        }
        colecao_usuarios.update_one({"_id": usuario["_id"]}, {"$push": {"favoritos": novo_favorito}})
        print(f"✅ Produto '{produto_escolhido['nome']}' adicionado aos favoritos!")

    elif escolha == '2':
        favoritos = usuario.get("favoritos", [])
        if not favoritos:
            print("Este usuário não tem produtos favoritos."); return
        
        print("\n--- Favoritos Atuais ---")
        for i, fav in enumerate(favoritos):
            print(f"{i + 1} - ID do Produto: {fav['id_produto']}")
        
        try:
            escolha_fav = int(input("Escolha o número do favorito para remover: ")) - 1
            favorito_a_remover = favoritos[escolha_fav]
        except (ValueError, IndexError):
            print("❌ Escolha inválida."); return
        
        colecao_usuarios.update_one({"_id": usuario["_id"]}, {"$pull": {"favoritos": {"id_produto": favorito_a_remover['id_produto']}}})
        print("✅ Favorito removido com sucesso!")

# FUNÇÕES CRUD PARA VENDEDORES E SEUS PRODUTOS

def criar_vendedor(colecao_vendedores, colecao_usuarios):
    print("\n--- 🧑‍💼 Adicionar Novo Vendedor ---")
    cpf_usuario = input("Digite o CPF do usuário que será o vendedor: ")
    usuario = colecao_usuarios.find_one({"cpf": cpf_usuario})
    if not usuario:
        print("❌ Usuário com este CPF não encontrado. Crie o usuário primeiro."); return
    
    reputacao = float(input("Digite a reputação do vendedor (ex: 4.8): "))
    novo_vendedor = {
        "id_vendedor": f"V{colecao_vendedores.count_documents({}) + 1}",
        "id_usuario": usuario.get("id_usuario"), # Link para o usuário
        "reputacao": reputacao,
        "produtos": []
    }
    colecao_vendedores.insert_one(novo_vendedor)
    print("✅ Vendedor criado e associado ao usuário com sucesso!")

def ler_vendedores(colecao_vendedores):
    print("\n--- 📋 Lista de Vendedores ---")
    if colecao_vendedores.count_documents({}) == 0:
        print("Nenhum vendedor encontrado."); return
    for vendedor in colecao_vendedores.find().sort("id_vendedor"):
        print(f"\n🧑‍💼 ID: {vendedor.get('id_vendedor')} | ID Usuário: {vendedor.get('id_usuario')} | Reputação: {vendedor.get('reputacao')} ⭐")
        if vendedor.get("produtos"):
            print("  📦 Produtos deste Vendedor:")
            for produto in vendedor["produtos"]:
                print(f"    - {produto['nome']} (Estoque: {produto['estoque']})")
        else:
            print("  (Nenhum produto cadastrado para este vendedor)")

# Funções de produtos embutidos
def adicionar_produto_a_vendedor(colecao_vendedores):
    print("\n--- 📦 Adicionar Produto a um Vendedor ---")
    id_vendedor = input("Digite o ID do Vendedor que receberá o produto: ")
    vendedor = colecao_vendedores.find_one({"id_vendedor": id_vendedor})
    if not vendedor:
        print("❌ Vendedor não encontrado."); return

    print("--- Preencha os dados do novo produto ---")
    nome = input("Nome do produto: ")
    descricao = input("Descrição (ex: i5, 8GB RAM): ")
    preco = float(input("Preço: "))
    categoria = input("Categoria (ex: Eletrônicos): ")
    estoque = int(input("Estoque: "))
    
    num_produtos = len(vendedor.get("produtos", []))
    id_produto = f"P{datetime.now().strftime('%f')}"

    novo_produto = {
        "id_produto": id_produto, "nome": nome, "descricao": descricao,
        "preco": preco, "categoria": categoria, "estoque": estoque
    }
    
    colecao_vendedores.update_one(
        {"id_vendedor": id_vendedor},
        {"$push": {"produtos": novo_produto}}
    )
    print(f"✅ Produto '{nome}' adicionado com sucesso ao vendedor {id_vendedor}!")

def atualizar_produto_de_vendedor(colecao_vendedores):
    print("\n--- 🔄 Atualizar Produto de um Vendedor ---")
    id_vendedor = input("Digite o ID do Vendedor: ")
    id_produto = input("Digite o ID do Produto a ser atualizado: ")

    query = {"id_vendedor": id_vendedor, "produtos.id_produto": id_produto}
    produto_existe = colecao_vendedores.find_one(query)
    if not produto_existe:
        print("❌ Produto ou Vendedor não encontrado."); return
    
    print("Deixe em branco para não alterar.")
    novo_preco_str = input("Novo preço: ")
    novo_estoque_str = input("Novo estoque: ")
    
    update_fields = {}
    if novo_preco_str: update_fields["produtos.$.preco"] = float(novo_preco_str)
    if novo_estoque_str: update_fields["produtos.$.estoque"] = int(novo_estoque_str)

    if not update_fields:
        print("Nenhuma alteração fornecida."); return
    
    colecao_vendedores.update_one(query, {"$set": update_fields})
    print("✅ Produto atualizado com sucesso!")


def remover_produto_de_vendedor(colecao_vendedores):
    print("\n--- 🗑️ Remover Produto de um Vendedor ---")
    id_vendedor = input("Digite o ID do Vendedor: ")
    id_produto = input("Digite o ID do Produto a ser removido: ")

    resultado = colecao_vendedores.update_one(
        {"id_vendedor": id_vendedor},
        {"$pull": {"produtos": {"id_produto": id_produto}}}
    )

    if resultado.modified_count > 0:
        print("✅ Produto removido com sucesso do vendedor!")
    else:
        print("❌ Produto ou Vendedor não encontrado.")


#  Lógica de Compra 
def comprar_produto(colecao_usuarios, colecao_vendedores):
    print("\n--- 🛒 Realizar uma Compra ---")
    cpf_comprador = input("Digite o CPF do usuário que está comprando: ")
    comprador = colecao_usuarios.find_one({"cpf": cpf_comprador})
    if not comprador:
        print("❌ Usuário comprador não encontrado."); return
    
    produtos_a_venda = []
    for vendedor in colecao_vendedores.find():
        for produto in vendedor.get("produtos", []):
            if produto.get("estoque", 0) > 0:
               
                produto['vendedor_id'] = vendedor['id_vendedor']
                produtos_a_venda.append(produto)
    
    if not produtos_a_venda:
        print("ℹ️ Nenhum produto disponível para compra."); return
    
    print("\n--- Produtos Disponíveis para Compra ---")
    for i, produto in enumerate(produtos_a_venda):
        print(f"{i + 1} - Produto: {produto['nome']} | Preço: R${produto['preco']:.2f} | Estoque: {produto['estoque']} | Vendedor: {produto['vendedor_id']}")
    
    try:
        escolha = int(input("\nDigite o número do produto que deseja comprar: ")) - 1
        produto_escolhido = produtos_a_venda[escolha]
        quantidade = int(input(f"Quantas unidades de '{produto_escolhido['nome']}' deseja comprar? "))
        if quantidade <= 0 or quantidade > produto_escolhido['estoque']:
            print("❌ Quantidade inválida ou insuficiente em estoque."); return
    except (ValueError, IndexError):
        print("❌ Entrada inválida."); return
        
    # Atualiza o estoque do produto embutido no vendedor
    colecao_vendedores.update_one(
        {"id_vendedor": produto_escolhido['vendedor_id'], "produtos.id_produto": produto_escolhido['id_produto']},
        {"$inc": {"produtos.$.estoque": -quantidade}}
    )
    
    valor_total = produto_escolhido['preco'] * quantidade
    nova_compra = {
        "id_compra": f"C{datetime.now().strftime('%f')}",
        "id_produto": produto_escolhido['id_produto'], "quantidade": quantidade,
        "valor_total": valor_total, "data_compra": datetime.now()
    }
    colecao_usuarios.update_one({"_id": comprador["_id"]}, {"$push": {"compras": nova_compra}})
    print(f"\n✅ Compra realizada com sucesso! Total: R${valor_total:.2f}")

 # ESTRUTURA DE MENUS 

def menu_usuario(colecao_usuarios, colecao_vendedores):
    while True:
        print("\n--- 👤 Menu do Usuário ---")
        print("1 - Criar Usuário"); print("2 - Listar Usuários"); print("3 - Gerenciar Favoritos ⭐"); print("V - Voltar")
        sub_choice = input("Opção: ").upper()
        if sub_choice == '1': criar_usuario(colecao_usuarios)
        elif sub_choice == '2': ler_usuarios(colecao_usuarios)
        elif sub_choice == '3': gerenciar_favoritos(colecao_usuarios, colecao_vendedores)
        elif sub_choice == 'V': break
        else: print("Opção inválida.")
        input("\nPressione Enter para continuar...")

def menu_vendedor(colecao_vendedores, colecao_usuarios):
    while True:
        print("\n--- 🧑‍💼 Menu de Vendedores e Produtos ---")
        print("1 - Criar Vendedor")
        print("2 - Listar Vendedores e seus Produtos")
        print("3 - Adicionar Produto a um Vendedor")
        print("4 - Atualizar Produto de um Vendedor")
        print("5 - Remover Produto de um Vendedor")
        print("V - Voltar")
        sub_choice = input("Opção: ").upper()
        if sub_choice == '1': criar_vendedor(colecao_vendedores, colecao_usuarios)
        elif sub_choice == '2': ler_vendedores(colecao_vendedores)
        elif sub_choice == '3': adicionar_produto_a_vendedor(colecao_vendedores)
        elif sub_choice == '4': atualizar_produto_de_vendedor(colecao_vendedores)
        elif sub_choice == '5': remover_produto_de_vendedor(colecao_vendedores)
        elif sub_choice == 'V': break
        else: print("Opção inválida.")
        input("\nPressione Enter para continuar...")

def main():
    usuarios, vendedores = conectar_db()
    if usuarios is None or vendedores is None:
        return

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("--- 🏪 MENU PRINCIPAL - GESTÃO MERCADO LIVRE ---")
        print("1 - 👤 Gerenciar Usuários")
        print("2 - 🧑‍💼 Gerenciar Vendedores e Produtos")
        print("3 - 🛒 Realizar uma Compra")
        print("S - ❌ Sair do programa")
        choice = input("Digite a opção desejada: ").upper()
        
        if choice == '1': menu_usuario(usuarios, vendedores)
        elif choice == '2': menu_vendedor(vendedores, usuarios)
        elif choice == '3': 
            comprar_produto(usuarios, vendedores)
            input("\nPressione Enter para continuar...")
        elif choice == 'S':
            print("\nPrograma finalizado. Até logo! 👋")
            break
        else:
            print("Opção inválida. Tente novamente.")
            input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()