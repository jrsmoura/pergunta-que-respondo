"""
Views para o aplicativo chatbot.
"""

from django.http import JsonResponse
from .rag_engine import answer_question
from django.shortcuts import render

def ask(request):
    """
    Lida com requisições GET para responder à pergunta de um usuário.
    Args:
        request (HttpRequest): O objeto de requisição HTTP contendo os parâmetros de consulta.
    Returns:
        JsonResponse: Uma resposta JSON contendo a pergunta original e sua resposta,
                      ou uma mensagem de erro se o parâmetro 'q' estiver ausente.
    """
    pergunta = request.GET.get("q", "")
    if not pergunta:
        return JsonResponse({"erro": "Informe a pergunta usando o parâmetro ?q="}, status=400)
    
    resposta = answer_question(pergunta)
    return JsonResponse({"pergunta": pergunta, "resposta": resposta})

def chat_interface(request):
    """
    Gerencia a interface de chat para a aplicação chatbot.

    Esta view controla a conversa entre o usuário e o chatbot, armazenando as mensagens na sessão.
    Suporta limpar a conversa e gerar respostas do bot para as perguntas do usuário.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.

    Returns:
        HttpResponse: A interface de chat renderizada com a conversa atual e o estado de "pensando".
    """
    if "messages" not in request.session:
        request.session["messages"] = []

    messages = request.session["messages"]
    thinking = False

    if request.method == "POST":
        if "clear" in request.POST:
            # botão limpar conversa
            request.session["messages"] = []
            messages = []
        else:
            pergunta = request.POST.get("pergunta")
            if pergunta:
                # adiciona pergunta do usuário
                messages.append({"sender": "user", "text": pergunta})
                request.session["messages"] = messages
                thinking = True

                # gera resposta do bot
                resposta = answer_question(pergunta)
                messages.append({"sender": "bot", "text": resposta})
                request.session["messages"] = messages

    return render(request, "chatbot/chat.html", {"messages": messages, "thinking": thinking})