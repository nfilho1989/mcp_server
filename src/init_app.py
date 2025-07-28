import sys
import time
import asyncio
from elasticsearch_client.es_client import ElasticsearchClient
from agents.elasticsearch_agent import main as simple_agent_main
from agents.elasticsearch_agent import main as agent_main
from mcp_server.server import MCPServer

def wait_for_elasticsearch(max_attempts=30):
    """Aguarda o Elasticsearch estar pronto"""
    print("Aguardando Elasticsearch iniciar...")
    
    client = ElasticsearchClient()
    attempts = 0
    
    while attempts < max_attempts:
        if client.check_connection():
            print("Elasticsearch está pronto!")
            return client
        
        attempts += 1
        print(f"   Tentativa {attempts}/{max_attempts}...")
        time.sleep(2)
    
    print("Timeout: Elasticsearch não respondeu")
    return None

def setup_elasticsearch():
    """Configura o Elasticsearch com dados iniciais"""
    client = wait_for_elasticsearch()
    
    if not client:
        return False
    
    print("\n Configurando Elasticsearch...")

    client.create_index() # Criar índice
    client.load_sample_data() # Carregar dados de exemplo
    stats = client.aggregate_by_category() # Mostrar estatísticas
    
    print(f"\n Estatísticas do índice:")
    for category, count in stats.items():
        print(f"   - {category}: {count} documentos")
    
    return True

def show_menu():
    """Mostra menu de opções"""
    print("\n" + "="*50)
    print("Sistema MCP + Elasticsearch + LangChain")
    print("="*50)
    print("\nEscolha uma opção:")
    print("1. Testar cliente Elasticsearch")
    print("2. Iniciar servidor MCP")
    print("3. Iniciar agente simplificado (recomendado)")
    print("4. Executar exemplo completo")
    print("5. Limpar dados")
    print("0. Sair")
    print("-"*50)

def test_elasticsearch():
    """Testa funcionalidades do Elasticsearch"""
        
    print("\n Testando Elasticsearch...")
    client = ElasticsearchClient()

    print("\n 1. Teste de busca por 'user':")
    results = client.search("user", size=3)
    for i, doc in enumerate(results, 1):
        print(f"   {i}. {doc['title'][:50]}...")
    
    print("\n2. Teste de agregação por categoria:")
    categories = client.aggregate_by_category()
    for cat, count in categories.items():
        print(f"   - {cat}: {count}")
    
    print("\n3. Teste de busca por ID (post_1):")
    doc = client.get_by_id("post_1")
    if doc:
        print(f"   Título: {doc['title']}")
        print(f"   Autor: {doc['metadata'].get('user_name', 'Unknown')}")

def start_mcp_server():
    """Inicia o servidor MCP"""
    print("\n Iniciando servidor MCP...")
    print("   (Pressione Ctrl+C para parar)")
    
   
    server = MCPServer()
    asyncio.run(server.run())

def start_ai_agent():
    """Inicia o agente de IA para chat"""
    print("\n Iniciando agente de IA...")
    agent_main()

def run_complete_example():
    """Executa um exemplo completo do sistema"""
    print("\n Executando exemplo completo...")
   
    client = ElasticsearchClient()
    total_docs = len(client.search("*", size=100))
    print(f"\n Total de documentos: {total_docs}")

    queries = [
        "posts sobre users",
        "email",
        "sunt aut facere"
    ]
    
    print("\n Exemplos de buscas:")
    for query in queries:
        results = client.search(query, size=2)
        print(f"\n   Query: '{query}'")
        print(f"   Resultados: {len(results)}")
        if results:
            print(f"   Primeiro resultado: {results[0]['title'][:60]}...")
    print("\n Demonstração do agente de IA:")
    print("   Para interagir com o agente, escolha a opção 3 no menu principal")
    
def start_simple_agent():
    """Inicia o agente simplificado"""
    print("\n Iniciando agente simplificado...")
    simple_agent_main()
    """Limpa todos os dados do Elasticsearch"""
    
    confirm = input("\n Tem certeza que deseja limpar todos os dados? (s/N): ")
    if confirm.lower() == 's':
        client = ElasticsearchClient()
        client.delete_index()
        print("Dados removidos com sucesso!")
    else:
        print("Operação cancelada")

def clear_data():
    """Limpa todos os dados do Elasticsearch"""
    
    confirm = input("\n Tem certeza que deseja limpar todos os dados? (s/N): ")
    if confirm.lower() == 's':
        client = ElasticsearchClient()
        client.delete_index()
        print("Dados removidos com sucesso!")
    else:
        print("Operação cancelada")

def main():
    """Função principal"""

    if not setup_elasticsearch():
        print("Erro ao configurar Elasticsearch")
        sys.exit(1)
    
    while True:
        show_menu()
        
        try:
            option = input("\nOpção: ").strip()
            
            if option == "0":
                print("\n Até logo!")
                break
            elif option == "1":
                test_elasticsearch()
            elif option == "2":
                start_mcp_server()
            elif option == "3":
                start_simple_agent()
            elif option == "4":
                run_complete_example()
            elif option == "5":
                clear_data()
            else:
                print("Opção inválida!")
            
            if option in ["1", "5", "6"]:
                input("\nPressione ENTER para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n Operação interrompida")
            continue
        except Exception as e:
            print(f"\n Erro: {e}")
            input("\nPressione ENTER para continuar...")

if __name__ == "__main__":
    main()