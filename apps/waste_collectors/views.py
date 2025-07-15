from django.shortcuts import render
from apps.waste_collectors.models import Collector
from django.db.models import Q

from django.shortcuts import render, get_object_or_404
from apps.waste_collectors.models import Collector, CollectorType

from django.http import JsonResponse
from django.db import transaction

from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from apps.users.models import User
from datetime import datetime
from django.views.decorators.http import require_POST
from apps.common.models import Address
import json


@login_required(login_url='login')
def collector_dashboard_view(request):
    query = request.GET.get("q", "")
    collectors = Collector.objects.select_related("collector_type", "user")

    if query:
        collectors = collectors.filter(
            Q(name__icontains=query) |
            Q(address_line_1__icontains=query) |
            Q(pin_code__icontains=query)
        )

    return render(request, "collectors/waste-collector-dashboard.html", {
        "collectors": collectors,
    })

@login_required
def edit_collector_view(request, collector_id):
    collector = get_object_or_404(Collector, id=collector_id)
    collector_types = CollectorType.objects.all()

    return render(request, "collectors/waste-collector-update.html", {
        "collector": collector,
        "collector_types": collector_types
    })

@require_POST
@transaction.atomic
def update_collector_view(request, collector_id):
    try:
        data = request.POST

        # Validate required fields
        required_fields = ["collector_name", "collector_type", "address_one", "city", "state", "zipcode", "collector_taxid", "created_date"]
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            return JsonResponse({
                "success": False,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, status=400)

        collector = get_object_or_404(Collector, id=collector_id)

        # Update data
        collector.name = data.get("collector_name").strip()
        collector_type = CollectorType.objects.filter(id=data.get("collector_type")).first()
        if not collector_type:
            return JsonResponse({"success": False, "message": "Invalid collector type"}, status=400)


        collector.address.address_line_1 = data.get("address_one", "").strip()
        collector.address.address_line_2 = data.get("address_two", "").strip()
        collector.address.city = data.get("city", "").strip()
        collector.address.state = data.get("state", "").strip()
        collector.address.pin_code = data.get("zipcode").strip()
        collector.address.save()
        collector.collector_type = collector_type
        collector.collector_create_date = parse_date(data.get("created_date"))
        collector.tax_id = data.get("collector_taxid", "").strip()
        collector.is_active = data.get("status") == "on"

        collector.save()

        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

    
@login_required
def collector_form_view(request):
    collector_types = CollectorType.objects.all()
    return render(request, "collectors/waste-collector-form.html", {
        "collector_types": collector_types
    })


@require_POST
@transaction.atomic
def create_collector_view(request):
    try:
        data = request.POST

        # Validate required fields
        required_fields = ["collector_name", "collector_type", "address_one", "city", "state", "zipcode", "collector_taxid", "created_date"]
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            return JsonResponse({
                "success": False,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, status=400)

        # Extract & validate fields
        name = data["collector_name"].strip()
        collector_type_id = data["collector_type"]
        tax_id = data["collector_taxid"].strip()
        created_date = parse_date(data["created_date"])
        is_active = data.get("status") == "on"

        # Get collector type
        collector_type = CollectorType.objects.filter(id=collector_type_id).first()
        if not collector_type:
            return JsonResponse({"success": False, "message": "Invalid collector type"}, status=400)
        
        address = Address.objects.create(
            address_line_1=data.get('address_one'),
            address_line_2=data.get('address_two'),
            city=data.get('city'),
            state=data.get('state'),
            pin_code=data.get('zipcode'),
        )

        # Save collector
        _ = Collector.objects.create(
            user=request.user,
            name=name,
            address=address,
            collector_type=collector_type,
            tax_id=tax_id,
            is_active=is_active,
            collector_create_date=created_date,
            updated_at=datetime.now()
        )
        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)



@login_required(login_url='login') 
def collector_type_form_add(request):
    # In the future, you can pass roles/statuses from DB like:
    roles = CollectorType.objects.all()
    statuses = ["active", "inactive"]

    context = {
        "page_title": "Add Collector Type",  # optional
        "roles": roles,
        "statuses": statuses,
    }
    return render(request, "collectors/waste-collector-type-form.html", context)


@require_POST
def assign_collector_type_ajax(request):
    role = request.POST.get("collector_type")

    if not role:
        return JsonResponse({"success": False, "message": "All fields are required."})

    try:
        _ = CollectorType.objects.get_or_create(name=role)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
    


@login_required
def collector_type_dashboard(request):
    collector_type_obj = CollectorType.objects.all()
    return render(request, "collectors/collector_type_dashboard.html", {
        "collector_type_obj":collector_type_obj
    })



@login_required(login_url='login')
def edit_collector_type_view(request, id):
    collector_type_id = id
    collector_type = get_object_or_404(CollectorType, id=collector_type_id)
    return render(request, "collectors/edit-collector-type.html", {
        "collector_type": collector_type,
    })


def update_collector_type(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            collector_type_name = data.get('collector_type')

            collector_type = get_object_or_404(CollectorType, pk=pk)

            if CollectorType.objects.filter(name=collector_type_name).exclude(pk=pk).exists():
                return JsonResponse({'status': 'error', 'message': 'Another CollectorType with this name already exists.'})

            collector_type.name = collector_type_name
            collector_type.save()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

