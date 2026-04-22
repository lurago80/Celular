import traceback
import uuid
import logging
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, OperationalError, DatabaseError
from django.contrib import messages
from django.template.loader import render_to_string

logger = logging.getLogger('core.erros')


def _traduzir_erro_banco(exception):
    """
    Retorna uma mensagem em português clara sobre o erro de banco de dados.
    Inspeciona a mensagem original para identificar padrões comuns do SQLite/Django.
    """
    msg = str(exception).lower()

    if isinstance(exception, IntegrityError):
        if 'unique' in msg or 'unique constraint' in msg:
            # Tenta extrair o campo do erro (ex: "UNIQUE constraint failed: core_cliente.cpf")
            campo = ''
            if 'failed:' in msg:
                parte = msg.split('failed:')[-1].strip()
                # pega só o nome da coluna (após o ponto)
                if '.' in parte:
                    campo = parte.split('.')[-1].split('\n')[0].strip()
                    campo = f' no campo "{campo}"'
            return (
                f'Registro duplicado{campo}: esse dado já existe no banco de dados. '
                f'Verifique se o {campo.strip() or "campo"} já foi cadastrado anteriormente.'
            )
        if 'not null' in msg or 'null constraint' in msg:
            return 'Campo obrigatório não preenchido. Verifique os dados do formulário.'
        if 'foreign key' in msg:
            return 'Não é possível salvar: referência a um registro que não existe (chave estrangeira inválida).'
        return f'Violação de integridade de dados: {str(exception)}'

    if isinstance(exception, OperationalError):
        if 'locked' in msg:
            return 'O banco de dados está ocupado no momento. Tente novamente em alguns segundos.'
        if 'no such table' in msg:
            return 'Tabela não encontrada no banco de dados. Execute as migrações (manage.py migrate).'
        if 'disk' in msg or 'full' in msg:
            return 'Sem espaço em disco para salvar os dados. Contate o administrador.'
        return f'Erro de acesso ao banco de dados: {str(exception)}'

    if isinstance(exception, ValidationError):
        # Django ValidationError pode ter mensagens estruturadas
        try:
            msgs = exception.message_dict
            linhas = []
            for campo, erros in msgs.items():
                linhas.append(f'{campo}: {", ".join(erros)}')
            return 'Dados inválidos — ' + ' | '.join(linhas)
        except AttributeError:
            return f'Dado inválido: {exception.message}'

    return f'Erro ao salvar no banco de dados: {str(exception)}'


class CapturarErrosMiddleware:
    """
    Middleware que captura todas as exceções não tratadas, gera um código de rastreio,
    registra em arquivo de log e exibe uma página de erro amigável ao usuário.

    Para erros de banco de dados em operações POST:
      - Mostra uma mensagem de erro clara na mesma página (via Django messages + redirect)
      - O usuário pode corrigir os dados e tentar novamente

    Para outros erros internos:
      - Exibe a página de erro completa com código de rastreio
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def _logar(self, request, exception, error_id, tb):
        usuario = str(request.user) if hasattr(request, 'user') else 'Anônimo'
        logger.error(
            f'\n{"="*60}\n'
            f'ERRO ID: [{error_id}]\n'
            f'URL: {request.method} {request.get_full_path()}\n'
            f'Usuário: {usuario}\n'
            f'IP: {request.META.get("REMOTE_ADDR", "?")}\n'
            f'Tipo: {type(exception).__name__}\n'
            f'Mensagem: {str(exception)}\n'
            f'{"="*60}\n'
            f'{tb}'
        )

    def process_exception(self, request, exception):
        # Deixa Django tratar 404 e 403 normalmente
        if isinstance(exception, Http404):
            return None
        if isinstance(exception, PermissionDenied):
            return None

        error_id = str(uuid.uuid4())[:8].upper()
        tb = traceback.format_exc()
        self._logar(request, exception, error_id, tb)

        # ── Erros de banco de dados em POST: redireciona de volta com mensagem clara ──
        erros_banco = (IntegrityError, OperationalError, DatabaseError, ValidationError)
        if isinstance(exception, erros_banco) and request.method == 'POST':
            mensagem_amigavel = _traduzir_erro_banco(exception)
            try:
                messages.error(
                    request,
                    f'{mensagem_amigavel} '
                    f'[Código de suporte: {error_id}]'
                )
                # Volta para a página que enviou o formulário (ou para o dashboard)
                destino = request.META.get('HTTP_REFERER') or request.get_full_path()
                return HttpResponseRedirect(destino)
            except Exception:
                pass  # se messages falhar, cai no handler genérico abaixo

        # ── Outros erros: página de erro completa com rastreio ──
        context = {
            'error_id': error_id,
            'error_message': str(exception),
            'error_type': type(exception).__name__,
            'traceback': tb,
            'path': request.get_full_path(),
            'method': request.method,
        }
        html = render_to_string('core/erro_interno.html', context, request=request)
        return HttpResponse(html, status=500)

