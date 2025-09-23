from django.http import JsonResponse
from .rag_engine import answer_question

def ask(request):
    pergunta = request.GET.get("q", "")
    if not pergunta:
        return JsonResponse({"erro": "Informe a pergunta usando o parâmetro ?q="}, status=400)
    
    resposta = answer_question(pergunta)
    return JsonResponse({"pergunta": pergunta, "resposta": resposta})
