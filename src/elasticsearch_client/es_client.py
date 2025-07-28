import json
import requests
from datetime import datetime
from elasticsearch import Elasticsearch
from typing import List, Dict, Any

class ElasticsearchClient:
    def __init__(self, host: str = "elasticsearch", port: int = 9200):
        """Inicializa o cliente Elasticsearch"""
        self.es = Elasticsearch([f"http://{host}:{port}"])
        self.index_name = "sample_data"
        
    def check_connection(self):
        """Verifica se o Elasticsearch está acessível"""
        try:
            info = self.es.info()
            print(f"Conectado ao Elasticsearch versão: {info['version']['number']}")
            return True
        except Exception as e:
            print(f"Erro ao conectar ao Elasticsearch: {e}")
            return False
    
    def create_index(self):
        """Cria o índice com mapeamento apropriado"""
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "category": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "metadata": {"type": "object"},
                    "embedding": {"type": "dense_vector", "dims": 384}
                }
            }
        }
        
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name, body=mapping)
            print(f"Índice '{self.index_name}' criado com sucesso!")
        else:
            print(f"Índice '{self.index_name}' já existe.")
    
    def load_sample_data(self):
        """Carrega dados de exemplo de uma API pública"""
        print("Carregando dados de exemplo...")
        
        # Usando a API JSONPlaceholder como exemplo
        try:
            # Buscar posts
            response = requests.get("https://jsonplaceholder.typicode.com/posts")
            posts = response.json()[:20]  # Limitar a 20 posts
            
            # Buscar usuários
            users_response = requests.get("https://jsonplaceholder.typicode.com/users")
            users = {user['id']: user for user in users_response.json()}
            
            # Indexar dados
            for post in posts:
                doc = {
                    "id": f"post_{post['id']}",
                    "title": post['title'],
                    "content": post['body'],
                    "category": "blog_post",
                    "tags": ["sample", "jsonplaceholder", f"user_{post['userId']}"],
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "metadata": {
                        "user_id": post['userId'],
                        "user_name": users.get(post['userId'], {}).get('name', 'Unknown'),
                        "user_email": users.get(post['userId'], {}).get('email', '')
                    }
                }
                
                self.es.index(index=self.index_name, id=doc['id'], body=doc)
            
            print(f"{len(posts)} documentos indexados com sucesso!")
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
    
    def search(self, query: str, size: int = 10) -> List[Dict[str, Any]]:
        """Realiza busca textual no Elasticsearch"""
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^2", "content", "tags"],
                    "type": "best_fields"
                }
            },
            "size": size
        }
        
        try:
            response = self.es.search(index=self.index_name, body=body)
            hits = response['hits']['hits']
            return [hit['_source'] for hit in hits]
        except Exception as e:
            print(f"Erro na busca: {e}")
            return []
    
    def get_by_id(self, doc_id: str) -> Dict[str, Any]:
        """Busca documento por ID"""
        try:
            response = self.es.get(index=self.index_name, id=doc_id)
            return response['_source']
        except Exception as e:
            print(f"Erro ao buscar documento: {e}")
            return {}
    
    def aggregate_by_category(self) -> Dict[str, int]:
        """Agrega documentos por categoria"""
        body = {
            "size": 0,
            "aggs": {
                "categories": {
                    "terms": {
                        "field": "category",
                        "size": 10
                    }
                }
            }
        }
        
        try:
            response = self.es.search(index=self.index_name, body=body)
            buckets = response['aggregations']['categories']['buckets']
            return {bucket['key']: bucket['doc_count'] for bucket in buckets}
        except Exception as e:
            print(f"Erro na agregação: {e}")
            return {}
    
    def delete_index(self):
        """Remove o índice (útil para testes)"""
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
            print(f"Índice '{self.index_name}' removido.")

# Teste do cliente
if __name__ == "__main__":
    client = ElasticsearchClient()
    
    if client.check_connection():
        client.create_index()
        client.load_sample_data()
        
        # Teste de busca
        results = client.search("user")
        print(f"\nResultados da busca por 'user': {len(results)} documentos encontrados")
        
        # Teste de agregação
        categories = client.aggregate_by_category()
        print(f"\nCategorias: {categories}")