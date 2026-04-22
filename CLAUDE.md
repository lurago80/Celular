# CLAUDE.md

## Sincronização automática com GitHub

Este projeto está configurado para:
- Manter um repositório remoto no GitHub: https://github.com/lurago80/Celular
- A cada alteração no projeto, atualizar automaticamente esse repositório.


### Como funciona
- Toda alteração feita no projeto será automaticamente commitada e enviada para o GitHub a cada minuto.
- Isso é feito por uma tarefa agendada do Windows que executa o script `sync_git.bat`.
- Este arquivo será atualizado sempre que as instruções mudarem.


### Como replicar manualmente (caso necessário)
1. Faça alterações no projeto.
2. Execute:
   ```sh
   git add .
   git commit -m "Atualização automática"
   git push
   ```

### Automação
- O script `sync_git.bat` faz commit e push automático de todas as alterações.
- Uma tarefa agendada chamada `SyncGitCelular` executa esse script a cada minuto.
- Para remover a automação, execute:
  ```sh
  schtasks /Delete /TN "SyncGitCelular" /F
  ```

---

*Gerenciado por GitHub Copilot (GPT-4.1)*
