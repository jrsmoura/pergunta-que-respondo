# agent_app/models.py
from django.db import models
from django.conf import settings

class Chat(models.Model):
    # agora o usuário é opcional (para visitantes)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,          # <- chave
        related_name="chats",
    )
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user or 'anon'}: {self.message[:30]}"
