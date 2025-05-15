from django.shortcuts import render
from django.db.models import Q
from apps.waste_generators.models import (
    Generator,
    WasteSourceMaster, 
    WasteSourceSpecificationMaster
)
from apps.waste_source_group.models import WasteGroupMaster, WasteGeneratorGroup
from apps.waste_generators.services import GeneratorService
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def generator_dashboard_view(request):
    query = request.GET.get("q", "")
    generators = GeneratorService.search_generators(query)
    return render(request, "generators/waste-generator-dashboard.html", {"generators": generators})


@login_required(login_url='login')
def generator_form_edit_view(request, pk=None):
    is_edit = pk is not None
    generator = get_object_or_404(Generator, pk=pk) if is_edit else None

    context = {
        "waste_groups": WasteGeneratorGroup.objects.all(),
        "sources": WasteSourceMaster.objects.all(),
        "specifications": WasteSourceSpecificationMaster.objects.all(),
        "generator": generator,
        "is_edit": is_edit,
        "page_title": "Edit Waste Generator" if is_edit else "Add Waste Generator"
    }
    return render(request, "generators/waste-generator-form.html", context)

@login_required(login_url='login')
def generator_form_view(request):
    context = {
        "waste_groups": WasteGeneratorGroup.objects.all()
    }
    return render(request, "generators/waste-generator-form.html", context)


def save_generator(request):
    if request.method == "POST":
        return GeneratorService.handle_submission(request)
    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)
