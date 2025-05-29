```markdown
# Projeto DDA Automatizado

Este projeto tem como objetivo automatizar a conciliação de dados financeiros entre os extratos do banco Safra e os relatórios do sistema Anita.

## Estrutura do Projeto

- `DDA_docker_auto.py`: Script para execução automatizada utilizando Docker.
- `extrato_safra.py`: Módulo responsável por processar os extratos do banco Safra.
- `relat_anita.py`: Módulo responsável por processar os relatórios do sistema Anita.
- `BD_cache.py`: Módulo para gerenciamento de logs de execução utilizando SQLite.
- `requirements.txt`: Arquivo com as dependências do projeto.
- `Dockerfile`: Arquivo de configuração para criação da imagem Docker.
- `Makefile`: Arquivo para facilitar a execução de comandos Docker.

- `DDA_project_auto_v2.py`: Arquivo para executar no terminal em loop infinito até que o usuário pare, com um timer de execução de 60s. (Arquivo atualizado, funciona como um backup caso o docker pare de funcionar)
- `DDA_docker_auto.py`: Arquivo arquivo deprecado para executar no terminal utilizando o watchdog para vigiar a pasta. (arquivo descontinuado)
- `DDA_project.py`: Arquivo para executar no terminal manualmente. (arquivo descontinuado)

## Dependências

As dependências do projeto estão listadas no arquivo `requirements.txt`. Para instalá-las, execute:

```sh
pip install -r requirements.txt
```

## Executando o Projeto

### Manualmente

Para executar o script principal manualmente, utilize:

```sh
python DDA_project_v2.py
```

### Utilizando Docker

!! ATENÇÃO O COMANDO MAKE DO MAKEFILE FUNCIONA APENAS NO LINUX ou no WSL !!

Para executar o projeto utilizando Docker, siga os passos abaixo:

1. Construa a imagem Docker:

```sh
make build
```

2. Execute o container:

```sh
make run
```

## Funcionalidades

- **Conciliação de Dados**: O script principal realiza a conciliação dos dados financeiros entre os extratos do banco Safra e os relatórios do sistema Anita.
- **Automatização**: Utilizando o script DDA_docker_auto.py, é possível automatizar a execução do projeto, monitorando uma pasta específica para novos arquivos e processando-os automaticamente.
- **Logs de Execução**: O módulo BD_cache.py gerencia os logs de execução, garantindo que arquivos já processados não sejam processados novamente.

## Instruções de Uso

1. Coloque os arquivos de extrato do banco Safra na pasta monitorada.
2. Execute o script principal ou utilize o Docker para automatizar o processo.
3. Insira a data de vencimento no formato `dd-mm-aaaa` quando solicitado.
4. O script irá processar os dados e gerar um relatório de conciliação em formato Excel.