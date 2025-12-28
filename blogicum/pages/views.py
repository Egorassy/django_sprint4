from django.views.generic import TemplateView
from django.shortcuts import render


class AboutPageView(TemplateView):
    template_name = "pages/about.html"


class RulesPageView(TemplateView):
    template_name = "pages/rules.html"


def custom_404_view(request, exception):
    return render(request, "pages/404.html", status=404)


def custom_403_view(request, exception):
    return render(request, "pages/403csrf.html", status=403)


def custom_500_view(request):
    return render(request, "pages/500.html", status=500)
