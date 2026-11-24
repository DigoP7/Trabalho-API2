from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Tarefa
from .serializers import TarefaSerializer


@api_view(["GET"])
def health(request):
    return Response({"status": "ok", "endpoints": 5})


@api_view(["GET"])
def listar_tarefas(request):
    tarefas = Tarefa.objects.all()
    return Response(TarefaSerializer(tarefas, many=True).data)


@api_view(["POST"])
def criar_tarefa(request):
    serializer = TarefaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH"])
def detalhe_atualizar_tarefa(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk)
    if request.method == "GET":
        return Response(TarefaSerializer(tarefa).data)
    serializer = TarefaSerializer(tarefa, data=request.data, partial=(request.method == "PATCH"))
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def excluir_tarefa(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk)
    tarefa.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def painel(request):
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Painel de Tarefas</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px; background: #f5f6f8; color: #1f2937; }
    .card { background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,.06); margin-bottom: 16px; }
    .top { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
    .badge { padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: bold; background: #dcfce7; color: #166534; }
    form { display: flex; gap: 8px; margin-top: 12px; }
    input[type="text"], input[type="search"] { flex: 1; padding: 10px; border: 1px solid #d1d5db; border-radius: 6px; box-sizing: border-box; }
    .search-box { width: 100%; margin-bottom: 12px; }
    button { padding: 10px 14px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
    .btn-add { background: #2563eb; color: #fff; }
    .btn-edit { background: #fef3c7; color: #92400e; }
    .btn-toggle { background: #e5e7eb; color: #111827; }
    .btn-del { background: #fee2e2; color: #991b1b; }
    ul { list-style: none; padding: 0; margin: 0; }
    li { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f0f0; gap: 10px; }
    li:last-child { border-bottom: none; }
    .done { text-decoration: line-through; color: #6b7280; }
    .actions { display: flex; gap: 6px; }
  </style>
</head>
<body>
  <div class="card">
    <div class="top">
      <h2 style="margin:0;">Painel de Tarefas</h2>
      <span id="status-api" class="badge">Verificando...</span>
    </div>
    <form id="form-criar">
      <input id="titulo" type="text" placeholder="Nova tarefa..." required />
      <button class="btn-add" type="submit">Adicionar</button>
    </form>
  </div>

  <div class="card">
    <h3 style="margin-top:0;">Lista (<span id="total">0</span>)</h3>
    <input id="busca" class="search-box" type="search" placeholder="Pesquisar tarefa pelo nome ou #id..." />
    <ul id="lista"></ul>
  </div>

  <script>
    let todasTarefas = [];

    async function verificarHealth() {
      const el = document.getElementById("status-api");
      try {
        const res = await fetch("/api/health/");
        const data = await res.json();
        el.textContent = "API " + data.status.toUpperCase() + " (" + data.endpoints + " endpoints)";
      } catch {
        el.textContent = "API OFFLINE";
      }
    }

    function renderizarLista() {
      const termo = document.getElementById("busca").value.trim().toLowerCase();
      const filtradas = todasTarefas.filter((t) => {
        if (!termo) return true;
        const textoId = ("#" + t.id).toLowerCase();
        return t.titulo.toLowerCase().includes(termo) || textoId.includes(termo) || String(t.id).includes(termo);
      });

      const ul = document.getElementById("lista");
      document.getElementById("total").textContent = filtradas.length + "/" + todasTarefas.length;
      ul.innerHTML = "";

      if (filtradas.length === 0) {
        ul.innerHTML = "<li style='color:#6b7280;'>Nenhuma tarefa encontrada.</li>";
        return;
      }

      for (const t of filtradas) {
        const li = document.createElement("li");
        const span = document.createElement("span");
        span.textContent = "#" + t.id + " - " + t.titulo;
        if (t.concluida) span.classList.add("done");

        const actions = document.createElement("div");
        actions.className = "actions";

        const btnEdit = document.createElement("button");
        btnEdit.className = "btn-edit";
        btnEdit.textContent = "Editar";
        btnEdit.onclick = async () => {
          const novoTitulo = prompt("Novo título da tarefa:", t.titulo);
          if (novoTitulo === null) return;
          const limpo = novoTitulo.trim();
          if (!limpo) return;
          await fetch("/api/tarefas/" + t.id + "/", {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ titulo: limpo })
          });
          carregarTarefas();
        };

        const btnToggle = document.createElement("button");
        btnToggle.className = "btn-toggle";
        btnToggle.textContent = t.concluida ? "Reabrir" : "Concluir";
        btnToggle.onclick = async () => {
          await fetch("/api/tarefas/" + t.id + "/", {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ concluida: !t.concluida })
          });
          carregarTarefas();
        };

        const btnDel = document.createElement("button");
        btnDel.className = "btn-del";
        btnDel.textContent = "Excluir";
        btnDel.onclick = async () => {
          await fetch("/api/tarefas/" + t.id + "/excluir/", { method: "DELETE" });
          carregarTarefas();
        };

        actions.append(btnEdit, btnToggle, btnDel);
        li.append(span, actions);
        ul.appendChild(li);
      }
    }

    async function carregarTarefas() {
      const res = await fetch("/api/tarefas/");
      todasTarefas = await res.json();
      renderizarLista();
    }

    document.getElementById("busca").addEventListener("input", renderizarLista);

    document.getElementById("form-criar").onsubmit = async (e) => {
      e.preventDefault();
      const input = document.getElementById("titulo");
      const titulo = input.value.trim();
      if (!titulo) return;
      await fetch("/api/tarefas/criar/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ titulo, concluida: false })
      });
      input.value = "";
      carregarTarefas();
    };

    verificarHealth();
    carregarTarefas();
  </script>
</body>
</html>"""
    return HttpResponse(html)
