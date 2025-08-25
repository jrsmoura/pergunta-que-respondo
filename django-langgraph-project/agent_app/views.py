from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from .models import Chat

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Carrega .env (opcional no Docker; ajuda no dev local)
load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if not GEMINI_API_KEY:
    # Se quiser só avisar no log em vez de quebrar:
    # print("WARN: GOOGLE_API_KEY não encontrada")
    raise RuntimeError("Faltou GOOGLE_API_KEY no ambiente.")

genai.configure(api_key=GEMINI_API_KEY)


def run_agent_view(message: str) -> str:
    """
    Chama o Gemini corretamente com o client oficial.
    Use 'gemini-1.5-flash' para respostas rápidas.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    # Opção simples:
    response = model.generate_content(message)
    text = getattr(response, "text", "") or ""
    return text.strip()

    # Se preferir chat com histórico:
    # chat = model.start_chat(history=[])
    # response = chat.send_message(message)
    # return (getattr(response, "text", "") or "").strip()


def chatbot(request):
    # Se não logado, mostramos histórico do "anônimo" (user=None)
    user_or_none = request.user if getattr(request.user, "is_authenticated", False) else None
    chats = Chat.objects.filter(user=user_or_none).order_by("-created_at")[:50]

    if request.method == "POST":
        message = (request.POST.get("message") or "").strip()
        if not message:
            return JsonResponse({"error": "Message cannot be empty."}, status=400)

        try:
            response = run_agent_view(message)
        except Exception as e:
            return JsonResponse({"error": f"Falha no modelo: {e}"}, status=500)

        Chat.objects.create(
            user=user_or_none,
            message=message,
            response=response,
            created_at=timezone.now(),
        )
        return JsonResponse({"message": message, "response": response})

    return render(request, "agent_app/chatbot.html", {"chats": chats})


