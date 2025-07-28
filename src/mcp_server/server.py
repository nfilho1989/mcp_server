import json
import asyncio
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from elasticsearch_client.es_client import ElasticsearchClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ToolType(Enum):
    SEARCH = "search"
    GET_BY_ID = "get_by_id"
    AGGREGATE = "aggregate"
    LIST_RECENT = "list_recent"

@dataclass
class Tool:
    name: str
    description: str
    parameters: Dict[str, Any]

@dataclass
class Resource:
    uri: str
    name: str
    description: str
    mime_type: str

class MCPServer:
    def __init__(self):
        self.es_client = ElasticsearchClient()
        self.tools = self._initialize_tools()
        self.resources = self._initialize_resources()
        
    def _initialize_tools(self) -> List[Tool]:
        """Define as ferramentas disponíveis"""
        return [
            Tool(
                name="search_documents",
                description="Busca documentos no Elasticsearch usando texto livre",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Texto de busca"
                        },
                        "size": {
                            "type": "integer",
                            "description": "Número máximo de resultados",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_document_by_id",
                description="Busca um documento específico por ID",
                parameters={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "ID do documento"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            Tool(
                name="aggregate_by_category",
                description="Obtém contagem de documentos por categoria",
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="list_recent_documents",
                description="Lista os documentos mais recentes",
                parameters={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Número de documentos a retornar",
                            "default": 5
                        }
                    },
                    "required": []
                }
            )
        ]
    
    def _initialize_resources(self) -> List[Resource]:
        """Define os recursos disponíveis"""
        return [
            Resource(
                uri="elasticsearch://sample_data/stats",
                name="Estatísticas do Índice",
                description="Estatísticas gerais sobre os dados indexados",
                mime_type="application/json"
            ),
            Resource(
                uri="elasticsearch://sample_data/schema",
                name="Schema do Índice",
                description="Estrutura e mapeamento do índice Elasticsearch",
                mime_type="application/json"
            )
        ]
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Manipula requisição de inicialização"""
        return {
            "protocolVersion": "0.1.0",
            "capabilities": {
                "tools": True,
                "resources": True,
                "prompts": False
            },
            "serverInfo": {
                "name": "elasticsearch-mcp-server",
                "version": "1.0.0"
            }
        }
    
    async def handle_list_tools(self) -> Dict[str, Any]:
        """Lista todas as ferramentas disponíveis"""
        tools_list = []
        for tool in self.tools:
            tools_list.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.parameters
            })
        
        return {"tools": tools_list}
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma ferramenta específica"""
        try:
            if name == "search_documents":
                query = arguments.get("query", "")
                size = arguments.get("size", 10)
                results = self.es_client.search(query, size)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "results": results,
                                "total": len(results),
                                "query": query
                            }, indent=2)
                        }
                    ]
                }
            
            elif name == "get_document_by_id":
                doc_id = arguments.get("document_id")
                result = self.es_client.get_by_id(doc_id)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            
            elif name == "aggregate_by_category":
                aggregations = self.es_client.aggregate_by_category()
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "categories": aggregations,
                                "total_categories": len(aggregations)
                            }, indent=2)
                        }
                    ]
                }
            
            elif name == "list_recent_documents":
                limit = arguments.get("limit", 5)
                # Busca documentos ordenados por data
                body = {
                    "query": {"match_all": {}},
                    "sort": [{"created_at": {"order": "desc"}}],
                    "size": limit
                }
                response = self.es_client.es.search(index=self.es_client.index_name, body=body)
                docs = [hit['_source'] for hit in response['hits']['hits']]
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "recent_documents": docs,
                                "count": len(docs)
                            }, indent=2)
                        }
                    ]
                }
            
            else:
                return {
                    "error": {
                        "code": "UNKNOWN_TOOL",
                        "message": f"Ferramenta '{name}' não encontrada"
                    }
                }
                
        except Exception as e:
            return {
                "error": {
                    "code": "TOOL_ERROR",
                    "message": str(e)
                }
            }
    
    async def handle_list_resources(self) -> Dict[str, Any]:
        """Lista todos os recursos disponíveis"""
        resources_list = []
        for resource in self.resources:
            resources_list.append({
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mime_type
            })
        
        return {"resources": resources_list}
    
    async def handle_read_resource(self, uri: str) -> Dict[str, Any]:
        """Lê um recurso específico"""
        try:
            if uri == "elasticsearch://sample_data/stats":
                stats = self.es_client.es.indices.stats(index=self.es_client.index_name)
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps({
                                "index": self.es_client.index_name,
                                "document_count": stats['_all']['primaries']['docs']['count'],
                                "size_in_bytes": stats['_all']['primaries']['store']['size_in_bytes'],
                                "categories": self.es_client.aggregate_by_category()
                            }, indent=2)
                        }
                    ]
                }
            
            elif uri == "elasticsearch://sample_data/schema":
                mapping = self.es_client.es.indices.get_mapping(index=self.es_client.index_name)
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(mapping[self.es_client.index_name], indent=2)
                        }
                    ]
                }
            
            else:
                return {
                    "error": {
                        "code": "RESOURCE_NOT_FOUND",
                        "message": f"Recurso '{uri}' não encontrado"
                    }
                }
                
        except Exception as e:
            return {
                "error": {
                    "code": "RESOURCE_ERROR",
                    "message": str(e)
                }
            }
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Processa mensagens JSON-RPC"""
        method = message.get("method")
        params = message.get("params", {})
        
        if method == "initialize":
            result = await self.handle_initialize(params)
        elif method == "tools/list":
            result = await self.handle_list_tools()
        elif method == "tools/call":
            result = await self.handle_call_tool(params.get("name"), params.get("arguments", {}))
        elif method == "resources/list":
            result = await self.handle_list_resources()
        elif method == "resources/read":
            result = await self.handle_read_resource(params.get("uri"))
        else:
            result = {
                "error": {
                    "code": "METHOD_NOT_FOUND",
                    "message": f"Método '{method}' não encontrado"
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": result
        }
    
    async def run(self):
        """Loop principal do servidor MCP"""
        print("Servidor MCP iniciado!")
        print("Conectando ao Elasticsearch...")
        
        if not self.es_client.check_connection():
            print("Falha ao conectar ao Elasticsearch")
            return
        
        self.es_client.create_index()
        self.es_client.load_sample_data()
        
        print("Servidor MCP pronto para receber requisições")
        print("Use o agente LangChain para interagir com o servidor")
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    server = MCPServer()
    asyncio.run(server.run())