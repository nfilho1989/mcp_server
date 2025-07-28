import os
import sys
import json
import re
from typing import List, Dict, Any
from langchain_community.llms import Ollama
from elasticsearch_client.es_client import ElasticsearchClient
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

class SimpleElasticsearchAgent:
    def __init__(self):
        self.es_client = ElasticsearchClient()
        self.llm = Ollama(
            model="mistral",
            temperature=0.5, 
            verbose=False 
        )
        
    def process_query(self, user_query: str) -> str:
        """Processa a pergunta do usuário de forma simples"""
        
        query_lower = user_query.lower()
        
        try:
            # 1. Busca por posts recentes
            if any(word in query_lower for word in ["recente", "recent", "último", "last", "novo", "new"]):
                return self._handle_recent_posts(user_query)
            
            # 2. Busca por categorias/estatísticas
            elif any(word in query_lower for word in ["categoria", "category", "estatística", "quantos", "distribuição"]):
                return self._handle_categories()
            
            # 3. Busca por ID específico
            elif "post_" in query_lower or "id" in query_lower:
                return self._handle_get_by_id(user_query)
            
            # 4. Busca geral
            else:
                return self._handle_search(user_query)
                
        except Exception as e:
            return f"Desculpe, ocorreu um erro: {str(e)}"
    
    def _handle_recent_posts(self, query: str) -> str:
        """Lista posts recentes"""
          
        numbers = re.findall(r'\d+', query)  
        limit = int(numbers[0]) if numbers else 5
        limit = min(limit, 20)
        
        body = {
            "query": {"match_all": {}},
            "sort": [{"created_at": {"order": "desc"}}],
            "size": limit
        }
        
        response = self.es_client.es.search(index=self.es_client.index_name, body=body)
        docs = [hit['_source'] for hit in response['hits']['hits']]
        
        if not docs:
            return "Nenhum documento encontrado."
        
        result = f"Os {len(docs)} posts mais recentes:\n\n"
        for i, doc in enumerate(docs, 1):
            result += f"{i}. **{doc['title']}**\n"
            result += f"   • ID: {doc['id']}\n"
            result += f"   • Autor: {doc['metadata'].get('user_name', 'Desconhecido')}\n"
            result += f"   • Criado: {doc['created_at'][:10]}\n"
            result += f"   • Prévia: {doc['content'][:80]}...\n\n"
        
        return result
    
    def _handle_categories(self) -> str:
        """Mostra estatísticas por categoria"""
        categories = self.es_client.aggregate_by_category()
        
        if not categories:
            return "Nenhuma categoria encontrada."
        
        total = sum(categories.values())
        result = "Distribuição de Documentos por Categoria:\n\n"
        
        for category, count in categories.items():
            percentage = (count / total) * 100
            bar = "█" * int(percentage / 5)  
            result += f"• {category}: {count} docs ({percentage:.1f}%)\n"
            result += f"  {bar}\n\n"
        
        result += f"Total: {total} documentos"
        return result
    
    def _handle_get_by_id(self, query: str) -> str:
        """Busca documento por ID"""

        match = re.search(r'post_\d+', query.lower())
        
        if not match:
            return "Por favor, especifique um ID válido (ex: post_1)"
        
        doc_id = match.group()
        doc = self.es_client.get_by_id(doc_id)
        
        if not doc:
            return f"Documento com ID '{doc_id}' não encontrado."
        
        result = f"**Detalhes do Documento**\n\n"
        result += f"**Título:** {doc['title']}\n"
        result += f"**ID:** {doc['id']}\n"
        result += f"**Autor:** {doc['metadata'].get('user_name', 'Desconhecido')}\n"
        result += f"**Email:** {doc['metadata'].get('user_email', 'N/A')}\n"
        result += f"**Categoria:** {doc['category']}\n"
        result += f"**Tags:** {', '.join(doc['tags'])}\n"
        result += f"**Criado em:** {doc['created_at'][:10]}\n\n"
        result += f"**Conteúdo:**\n{doc['content']}\n"
        
        return result
    
    def _handle_search(self, query: str) -> str:
        """Busca geral"""
        prompt = f"Extraia as palavras-chave principais desta pergunta (responda apenas com as palavras, separadas por espaço): {query}"
        try:
            keywords = self.llm.invoke(prompt).strip()
        except:
            keywords = query # Fallback: usar a query original
        
        results = self.es_client.search(keywords, size=5)
        
        if not results:
            return f"Nenhum resultado encontrado para: {keywords}"
        
        result = f"Encontrados {len(results)} resultados para '{keywords}':\n\n"
        
        for i, doc in enumerate(results, 1):
            result += f"{i}. **{doc['title']}**\n"
            result += f"   • ID: {doc['id']}\n"
            result += f"   • Autor: {doc['metadata'].get('user_name', 'Desconhecido')}\n"
            result += f"   • Prévia: {doc['content'][:100]}...\n\n"
        
        return result
    
    def chat(self, message: str) -> str:
        """Interface principal de chat"""
        return self.process_query(message)

def main():
    """Função principal para executar o agente"""
    print("Iniciando Agente Simplificado para Elasticsearch...")
    
    agent = SimpleElasticsearchAgent()

    if not agent.es_client.check_connection():
        print("Erro: Não foi possível conectar ao Elasticsearch")
        return
    
    print("Agente iniciado com sucesso!")
    print("Digite suas perguntas (ou 'sair' para encerrar)")
    print("\n Exemplos de perguntas:")
    print("   - Me mostre os 3 posts mais recentes")
    print("   - Quantos documentos temos por categoria?")
    print("   - Busque posts sobre user")
    print("   - Me dê detalhes do post_1")
    print("-" * 50)
    
    while True:
        user_input = input("\n Você: ").strip()
        
        if user_input.lower() in ['sair', 'exit', 'quit']:
            print("Até logo!")
            break
        
        print("\n Assistente: ")
        response = agent.chat(user_input)
        print(response)

if __name__ == "__main__":
    main()