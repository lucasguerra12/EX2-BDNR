import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import os
import hashlib 
from datetime import datetime

# Conexão
uri = "mongodb+srv://lucasguerra:lucasguerra@projetoloja.11g2zmw.mongodb.net/"

def conectar_db():
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        db = client["mercadolivre_ex2"] # Banco específico para o EX2
        return db.usuarios, db.vendedores, db.produtos
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return None, None, None

# ==============================================================================
# 👤 CRUD USUÁRIOS (Insert, Read, Update, Delete)
# ==============================================================================

def criar_usuario(col_usuarios):
    print("\n--- 👤 Criar Usuário ---")
    nome = input("Nome: ")
    cpf = input("CPF: ")
    email = input("E-mail: ")
    
    usuario = {
        "nome": nome, "cpf": cpf, "email": email,
        "favoritos": [], "compras": []
    }
    col_usuarios.insert_one(usuario)
    print("✅ Insert realizado em Usuários!")

def ler_usuarios(col_usuarios): # (Search)
    print("\n--- 📋 Listar Usuários ---")
    for u in col_usuarios.find():
        print(f"ID: {u['_id']} | Nome: {u['nome']} | CPF: {u['cpf']}")

def atualizar_usuario(col_usuarios): # (Update)
    cpf = input("Digite o CPF do usuário para atualizar: ")
    query = {"cpf": cpf}
    
    if col_usuarios.count_documents(query) == 0:
        print("❌ Usuário não encontrado."); return

    novo_nome = input("Novo Nome (Enter para manter): ")
    novo_email = input("Novo Email (Enter para manter): ")
    
    update_data = {}
    if novo_nome: update_data["nome"] = novo_nome
    if novo_email: update_data["email"] = novo_email
    
    if update_data:
        col_usuarios.update_one(query, {"$set": update_data})
        print("✅ Update realizado em Usuários!")
    else:
        print("Nenhuma alteração feita.")

def deletar_usuario(col_usuarios): # (Delete)
    cpf = input("Digite o CPF do usuário para deletar: ")
    res = col_usuarios.delete_one({"cpf": cpf})
    if res.deleted_count > 0:
        print("✅ Delete realizado em Usuários!")
    else:
        print("❌ Usuário não encontrado.")

# ==============================================================================
# 🧑‍💼 CRUD VENDEDORES (Insert, Read, Update, Delete)
# ==============================================================================

def criar_vendedor(col_vendedores):
    print("\n--- 🧑‍💼 Criar Vendedor ---")
    empresa = input("Nome da Empresa: ")
    cnpj = input("CNPJ: ")
    
    vendedor = {"empresa": empresa, "cnpj": cnpj, "reputacao": 5.0}
    col_vendedores.insert_one(vendedor)
    print("✅ Insert realizado em Vendedores!")

def ler_vendedores(col_vendedores): # (Search)
    print("\n--- 📋 Listar Vendedores ---")
    for v in col_vendedores.find():
        print(f"ID: {v['_id']} | Empresa: {v['empresa']} | CNPJ: {v['cnpj']}")

def atualizar_vendedor(col_vendedores): # (Update)
    cnpj = input("CNPJ do vendedor para atualizar: ")
    novo_nome = input("Novo Nome da Empresa: ")
    
    res = col_vendedores.update_one({"cnpj": cnpj}, {"$set": {"empresa": novo_nome}})
    if res.modified_count > 0:
        print("✅ Update realizado em Vendedores!")
    else:
        print("❌ Vendedor não encontrado ou sem alterações.")

def deletar_vendedor(col_vendedores): # (Delete)
    cnpj = input("CNPJ do vendedor para deletar: ")
    res = col_vendedores.delete_one({"cnpj": cnpj})
    if res.deleted_count > 0:
        print("✅ Delete realizado em Vendedores!")
    else:
        print("❌ Vendedor não encontrado.")

# ==============================================================================
# 📦 CRUD PRODUTOS (Insert, Read, Update, Delete)
# ==============================================================================

def criar_produto(col_produtos, col_vendedores):
    print("\n--- 📦 Criar Produto ---")
    cnpj_vendedor = input("CNPJ do Vendedor dono do produto: ")
    vendedor = col_vendedores.find_one({"cnpj": cnpj_vendedor})
    
    if not vendedor:
        print("❌ Vendedor não existe. Crie-o primeiro."); return

    nome = input("Nome do Produto: ")
    preco = float(input("Preço: "))
    
    produto = {
        "nome": nome, "preco": preco, "estoque": 10,
        "vendedor_id": vendedor["_id"],
        "vendedor_nome": vendedor["empresa"]
    }
    col_produtos.insert_one(produto)
    print("✅ Insert realizado em Produtos!")

def ler_produtos(col_produtos): # (Search)
    print("\n--- 📦 Listar Produtos ---")
    for p in col_produtos.find():
        print(f"Produto: {p['nome']} | R${p['preco']} | Loja: {p.get('vendedor_nome')}")

def atualizar_produto(col_produtos): # (Update)
    nome = input("Nome do produto para atualizar preço: ")
    novo_preco = float(input("Novo Preço: "))
    
    res = col_produtos.update_one({"nome": nome}, {"$set": {"preco": novo_preco}})
    if res.modified_count > 0:
        print("✅ Update realizado em Produtos!")
    else:
        print("❌ Produto não encontrado.")

def deletar_produto(col_produtos): # (Delete)
    nome = input("Nome do produto para deletar: ")
    res = col_produtos.delete_one({"nome": nome})
    if res.deleted_count > 0:
        print("✅ Delete realizado em Produtos!")
    else:
        print("❌ Produto não encontrado.")

# ==============================================================================
# MENU PRINCIPAL
# ==============================================================================

def main():
    usuarios, vendedores, produtos = conectar_db()
    if usuarios is None: return

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=== EXERCÍCIO 2: CRUD COMPLETO (MongoDB) ===")
        print("1. 👤 Usuário: Criar")
        print("2. 👤 Usuário: Listar")
        print("3. 👤 Usuário: Atualizar (UPDATE)")
        print("4. 👤 Usuário: Deletar (DELETE)")
        print("--------------------------------")
        print("5. 🧑‍💼 Vendedor: Criar")
        print("6. 🧑‍💼 Vendedor: Listar")
        print("7. 🧑‍💼 Vendedor: Atualizar (UPDATE)")
        print("8. 🧑‍💼 Vendedor: Deletar (DELETE)")
        print("--------------------------------")
        print("9. 📦 Produto: Criar")
        print("10. 📦 Produto: Listar")
        print("11. 📦 Produto: Atualizar (UPDATE)")
        print("12. 📦 Produto: Deletar (DELETE)")
        print("0. Sair")
        
        op = input("Escolha: ")

        # Usuários
        if op == '1': criar_usuario(usuarios)
        elif op == '2': ler_usuarios(usuarios)
        elif op == '3': atualizar_usuario(usuarios)
        elif op == '4': deletar_usuario(usuarios)
        
        # Vendedores
        elif op == '5': criar_vendedor(vendedores)
        elif op == '6': ler_vendedores(vendedores)
        elif op == '7': atualizar_vendedor(vendedores)
        elif op == '8': deletar_vendedor(vendedores)

        # Produtos
        elif op == '9': criar_produto(produtos, vendedores)
        elif op == '10': ler_produtos(produtos)
        elif op == '11': atualizar_produto(produtos)
        elif op == '12': deletar_produto(produtos)
        
        elif op == '0': break
        else: print("Opção inválida")
        
        input("\nEnter para continuar...")

if __name__ == "__main__":
    main()