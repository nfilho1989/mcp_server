@echo off
echo Criando estrutura de diretorios...

mkdir src
mkdir data
mkdir notebooks
mkdir src\mcp_server
mkdir src\elasticsearch_client
mkdir src\agents

echo Estrutura criada com sucesso!

echo.
echo Arquivos necessarios:
echo - Dockerfile
echo - requirements.txt
echo - docker-compose.yml
echo.
echo Certifique-se de que todos os arquivos estao no diretorio:
echo D:\6. Trabalho\5. Afya\model_context_protocol-elascticsearch\mcp_server
echo.
pause