from django.urls import path
from . import views

urlpatterns = [
    path("", views.painel),
    path("health/", views.health),
    path("tarefas/", views.listar_tarefas),
    path("tarefas/criar/", views.criar_tarefa),
    path("tarefas/<int:pk>/", views.detalhe_atualizar_tarefa),
    path("tarefas/<int:pk>/excluir/", views.excluir_tarefa),
    path("painel/", views.painel),
]
