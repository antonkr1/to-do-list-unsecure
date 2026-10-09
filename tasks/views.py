import logging
import os
import secrets

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import format_html, format_html_join
from django.views.decorators.http import require_GET, require_http_methods

from .forms import TaskForm
from .models import Task

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def index(request):
    form = TaskForm()

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            logger.info("Tache ajoutee : %s", task.title)
        return redirect("/")

    context = {"tasks": Task.objects.all(), "form": form}
    return render(request, "tasks/list.html", context)


@require_http_methods(["GET", "POST"])
def update_task(request, pk):
    task = get_object_or_404(Task, id=pk)
    form = TaskForm(instance=task)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            logger.info("Tache modifiee : %s", task.title)
            return redirect("/")

    return render(request, "tasks/update_task.html", {"form": form})


@require_http_methods(["GET", "POST"])
def delete_task(request, pk):
    item = get_object_or_404(Task, id=pk)

    if request.method == "POST":
        item.delete()
        logger.info("Tache supprimee : %s", item.title)
        return redirect("/")

    return render(request, "tasks/delete.html", {"item": item})


@require_GET
def search_tasks(request):
    query = request.GET.get("q", "")
    tasks = Task.objects.filter(title__icontains=query)
    items = format_html_join("", "<li>{}</li>", ((t.title,) for t in tasks))
    return HttpResponse(format_html("<ul>{}</ul>", items))


@require_GET
def admin_panel(request):
    expected = os.environ.get("APP_ADMIN_PASSWORD")
    provided = request.GET.get("pwd", "")
    if not expected or not secrets.compare_digest(provided, expected):
        raise Http404
    return HttpResponse("Bienvenue admin !")
