## Tarefas do dia


- [x] adicionar botão para baixar do banco de dados - Feito!
- [x] Adicionar rota para deletar tudo - Feito!
- [x] Não inserir novamente no banco de dados se os dados da sku for igual - Feito!
- [x] testar upload de dados
- [x] Checar antes de extrair se o link ja existe no banco de dados
    - [x] Criar botão de atualizar e extrair separado
    - [x] Adicionar rota para atualizar 
        - [x] Podendo atualizar diretamente, ou inserindo sku para atualizar
        - [x] usar uma thread separada para atualizar os produtos
        - [ ] notificar via e-mail se concluiu com exito

- [x] testar banco de dados com socket - Feito!
- [ ] garantir que o processo rode independente:
    - [ ] Desavitar tempo de login do wordpress
    - [ ] Não usar muitos links de uma vez para evitar bloqueio

- [x] add error handler on socket
- [x] add 2nd list of links to test
- [x] add client list to test
- [x] change to prod database
    - [x] use another instance of database
    - [x] add .env to update database
    - [ ] make the client create new database or create new database for given id
- [x] add delete by sku
- [x] add change product link
- [x] add amazon code on description
- [ ] add keys to app
- [ ] fix price on aliexpress
- [ ] change to dev database

## BUGS
- [x] Socket não emite quando reseta o navegador
- [x] Reconectar ao estado atual quando recarregar página
- [x] Amazon Stale element... - Ocasional, depende da internet
- [x] promotional price is string
- [x] update running on multitread instead of on process by time