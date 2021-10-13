## Tarefas do dia

- [ ] adicionar botão para baixar do banco de dados - Feito!
- [ ] Adicionar rota para deletar tudo - Feito!
- [ ] Não inserir novamente no banco de dados se os dados da sku for igual - Feito!
- [ ] Não inserir novamente no banco de dados se os dados do link for igual
    - [ ] Criar botão de atualizar e extrair separado
    - [ ] Adicionar rota para atualizar 
        - [ ] Podendo atualizar diretamente, ou inserindo sku para atualizar
        - [ ] usar uma thread separada para atualizar os produtos
        - [ ] notificar via e-mail se concluiu com exito

- testar banco de dados com socket - Feito!
- deploy
- garantir que o processo rode independente:
    - Desavitar tempo de login do wordpress
    - Não usar muitos links de uma vez para evitar bloqueio

## BUGS
    - Socket não emite quando reseta o navegador
    - Reconectar ao estado atual quando recarregar página
    - Amazon Stale element... - Ocasional, depende da internet