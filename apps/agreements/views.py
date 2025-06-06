from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from datetime import date
from django.db.models import Q
from django.db import transaction
from dateutil.relativedelta import relativedelta  # make sure python-dateutil is installed

from apps.agreements.models import Agreement
from apps.waste_collectors.models import Collector
from apps.waste_generators.models import WasteSourceMaster
from s3 import upload_file_to_s3_fileobj


@login_required(login_url='login') 
def agreement_dashboard_view(request):
    query = request.GET.get("q", "").strip()

    agreements = Agreement.objects.select_related('generator', 'collector', 'generator__waste_source')

    if query:
        agreements = agreements.filter(
            Q(generator__waste_source__name__icontains=query) |
            Q(collector__name__icontains=query)
        )

    agreements = agreements.only(
        'id', 'generator__id', 'generator__waste_source__name', 'generator__address', 'collector__name', 'agreement_paper', 'expiration_date')

    results = []
    for agreement in agreements:
        file_name = agreement.agreement_paper.name.split('/')[-1] if agreement.agreement_paper else ''
        file_url = agreement.agreement_paper if agreement.agreement_paper else ''

        results.append({
            "id": agreement.id,
            "generator_id": str(agreement.generator.id),
            "generator_name": agreement.generator.waste_source.name,
            "collector_name": agreement.collector.name,
            "agreement_file_name": file_name,
            "agreement_file_url": file_url,
            "agreement_expiry_date": agreement.expiration_date.strftime("%Y-%m-%d") if agreement.expiration_date else None,
        })

    return render(request, "agreements/agreement-dashboard.html", {
        "agreements": results,
        "search_query": query
    })

@login_required(login_url='login') 
def agreement_form_view(request):
    generators= WasteSourceMaster.objects.all().select_related('waste_source', 'address')
    collectors = Collector.objects.all().only('id', 'name')

    context = {
        "generators": generators,
        "collectors": collectors,
    }
    return render(request, "agreements/agreement-form.html", context)

@require_POST
def agreement_ajax_submit(request):
    try:
        gen_id = request.POST.get("waste_generator")
        col_id = request.POST.get("waste_collector")
        file = request.FILES.get("agreement_file")
        expiray_date = request.POST.get("expiration_date")
        Notes = request.POST.get("notes")

        if not (gen_id and col_id and file):
            return JsonResponse({"success": False, "message": "All fields are required."})
            
        file = upload_file_to_s3_fileobj(file, 'agreements')
        start_date = date(2025, 4, 1)
        end_date = start_date + relativedelta(years=99)

        generator= WasteSourceMaster.objects.get(id=gen_id)
        collector = Collector.objects.get(id=col_id)
        with transaction.atomic():
            _ = Agreement.objects.create(
                generator = generator,
                collector = collector,
                start_date = start_date,
                end_date = end_date,
                expiration_date = expiray_date,
                notes = Notes,
                is_active=True,
                agreement_paper = file
            )
        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})

@login_required(login_url='login')
def agreement_edit_form(request, id):
    generators= WasteSourceMaster.objects.all().select_related('waste_source', 'address')
    collectors = Collector.objects.all().only('id', 'name')

    agreemnt = Agreement.objects.get(id=id)
    context = {
        'generators': generators,
        'collectors': collectors,
        'agreemnt':agreemnt
    }

    return render(request, 'agreements/agreement-edit-form.html', context)


@require_POST
def agreement_ajax_update(request):
    try:
        agreement_id = request.POST.get("agreement_id")
        gen_id = request.POST.get("waste_generator")
        col_id = request.POST.get("waste_collector")
        file = request.FILES.get("agreement_file")
        file = upload_file_to_s3_fileobj(file, 'agreements')


        if not agreement_id:
            return JsonResponse({"success": False, "message": "Agreement ID is required."})

    

        if not (gen_id and col_id):
            return JsonResponse({"success": False, "message": "Generator and Collector are required."})

        agreement = Agreement.objects.get(id=agreement_id)
        agreement.generator = WasteSourceMaster.objects.get(id=gen_id)
        agreement.collector = Collector.objects.get(id=col_id)

        # Optional: Update file only if a new one is uploaded
        if file:
            agreement.agreement_paper = file

        agreement.save()

        return JsonResponse({"success": True, "message": "Agreement updated successfully."})

    except Agreement.DoesNotExist:
        return JsonResponse({"success": False, "message": "Agreement not found."})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
