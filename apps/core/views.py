from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST
from django.core.files.storage import FileSystemStorage
from apps.core.models import MeasuringUnitMaster, CommodityMater, CommodityGroup
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q

from django.views.decorators.csrf import csrf_exempt
import pandas as pd, json


@login_required(login_url='login') 
def master_commodity_dashboard(request):
    query = request.GET.get("q", "").strip()
    
    commodities = CommodityMater.objects.filter(created_user=request.user).select_related('measuring_unit', 'group')

    if query:
        commodities = commodities.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(measuring_unit__name__icontains=query) |
            Q(group__name__icontains=query)
        )

    return render(request, "masters/master-commodity-dashboard.html", {
        "commodities": commodities,
        "search_query": query
    })

@login_required(login_url='login') 
def commodity_form_view(request):
    units = MeasuringUnitMaster.objects.values('id','name')
    commoditi_group = CommodityGroup.objects.all()
    return render(request, "masters/master-commodity-form.html", {
        "units": units,
        "commoditi_group": commoditi_group
    })

@require_http_methods(["POST"])
def add_commodity_ajax(request):
    try:
        name = request.POST.get("commodity_name")
        group = request.POST.get("commodity_group")
        sub = request.POST.get("sub_commodity")
        unit = request.POST.get("commodity_unit")
        active = request.POST.get("active_status")

        if not (name and group and sub and unit):
            return JsonResponse({"success": False, "message": "All fields are required."})

        unit = MeasuringUnitMaster.objects.get(id=unit)
        commoditi_group = CommodityGroup.objects.get(id=group)
        active = 'A' if active == 'on' else 'I'
        with transaction.atomic():
            CommodityMater.objects.create(
                name=name,
                group=commoditi_group,
                sub_commodity=sub,
                measuring_unit=unit,
                status=active,
                created_user=request.user,
            )

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})

@require_POST
def upload_commodity_document(request):
    try:
        file = request.FILES.get("supporting_document")

        if not file:
            return JsonResponse({"success": False, "message": "No file uploaded."})

        if file.size > 10 * 1024 * 1024:
            return JsonResponse({"success": False, "message": "File must be under 10MB."})

        fs = FileSystemStorage(location="media/commodity_docs/")
        filename = fs.save(file.name, file)
        file_url = fs.url(filename)

        return JsonResponse({
            "success": True,
            "file_name": filename,
            "file_url": file_url
        })

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})

@login_required(login_url='login')  
def unit_form_view(request):
    return render(request, "masters/unit-form.html")

@require_http_methods(["POST"])
def add_unit_ajax(request):
    name = request.POST.get("unit_name", "").strip()
    
    if not name:
        return JsonResponse({"success": False, "message": "Unit name is required."})
    
    if MeasuringUnitMaster.objects.filter(name__iexact=name).exists():
        return JsonResponse({"success": False, "message": "Unit already exists."})

    with transaction.atomic():
        MeasuringUnitMaster.objects.create(name=name)
    return JsonResponse({"success": True})

@login_required(login_url='login')
def edit_commodity_view(request, id):
    commodity_id = id
    commodity = get_object_or_404(CommodityMater, id=commodity_id)
    units = MeasuringUnitMaster.objects.filter(status='A')
    commoditi_group = CommodityGroup.objects.all()
    return render(request, "masters/master-commodity-edit-form.html", {
        "commodity": commodity,
        "units": units,
        'groups': commoditi_group
    })


def update_commodity(request):
    try:
        data = request.POST
        commodity_id = data.get("id")
        commodity = get_object_or_404(CommodityMater, id=commodity_id)

        with transaction.atomic():
            commodity.name = data.get("commodity_name").strip()
            #commodity.description = data.get("sub_commodity").strip()
            commodity.status = 'A' if data.get("active_status") == 'on' else 'I'
            unit_id = data.get("commodity_unit")

            if unit_id:
                commodity.measuring_unit_id = unit_id

            commodity.save()

        return JsonResponse({"success": True, "message": "Commodity updated successfully!"})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})



@login_required(login_url='login') 
def commodity_bulk_import_view(request):
    return render(request, "masters/commodity-import-form.html") 

@csrf_exempt
def upload_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        excel_file = request.FILES['file']
        df = pd.read_excel(excel_file)

        # Step 1: Extract headers from uploaded Excel
        file_columns = list(df.columns)

        # Step 2: Extract model field names
        model_fields = [field.name for field in CommodityMater._meta.fields if field.name != "id"]

        # Step 3: Define mandatory fields (customize as needed)
        # mandatory_fields = ["collector_type", "address"]

        # Convert DataFrame rows to a list of dicts
        data_rows = []
        for _, row in df.iterrows():
            data_rows.append({"list": row.to_dict()})


        # Step 4: Prepare the JSON response
        response_data = {
            "localization": {},
                "options": {
                    "associationMode": "oneToOne", # oneToOne,manyToMany
                    "lineStyle": "square-ends",
                    "buttonErase": "Erase Links",
                    "displayMode": "original",
                    # "whiteSpace": $("input[name='whiteSpace']:checked").val(),
                    "mobileClickIt": False
                },
            "Lists": [
                {
                    "name": "Columns in files",
                    "list": file_columns
                },
                {
                    "name": "Available Fields",
                    "list": model_fields,
                    # "mandatories": mandatory_fields
                }
            ],
            "data": data_rows
        }

        return JsonResponse(response_data)
    
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def add_commodities_form(request):
    return render(request, "masters/add-commoditi.html")

@login_required
def commodities_type_dashboard(request):
    commoditi_objs = CommodityGroup.objects.all()
    return render(request, "masters/commoties-dashboard.html", {
        "commoditi_objs":commoditi_objs
    })

def create_commodity_type(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('commodity_name')
            code = data.get('commodity_code')
            active_status = data.get('active_status', 'A')

            if not name or not code:
                return JsonResponse({'status': 'error', 'message': 'Name and code are required.'})

            # Check for duplicate
            if CommodityGroup.objects.filter(name=name).exists():
                return JsonResponse({'status': 'error', 'message': 'Commodity with this name already exists.'})

            with transaction.atomic():
                CommodityGroup.objects.create(
                    name=name,
                    code=code,
                    status=active_status
                )
            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required(login_url='login')
def edit_commodity_type_page(request, pk):
    commodity = get_object_or_404(CommodityGroup, pk=pk)
    return render(request, 'masters/edit-commoditi-type.html', {'commodity': commodity})

def edit_commodity_type(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('commodity_name')
            code = data.get('commodity_code')
            active_status = data.get('active_status', 'A')

            if not name or not code:
                return JsonResponse({'status': 'error', 'message': 'Name and code are required.'})

            commodity = get_object_or_404(CommodityGroup, pk=pk)

            if CommodityGroup.objects.filter(name=name).exclude(pk=pk).exists():
                return JsonResponse({'status': 'error', 'message': 'Another commodity with this name already exists.'})

            commodity.name = name
            commodity.code = code
            commodity.status = active_status
            commodity.save()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})