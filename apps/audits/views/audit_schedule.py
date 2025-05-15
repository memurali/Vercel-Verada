from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.audits.models import Audit
from datetime import datetime
from django.contrib.auth.decorators import login_required
from apps.audits.models import Official
from apps.common.services.async_email import AsyncEmailSender
from apps.waste_source_group.models import MasterSource
from apps.waste_generators.models import WasteSourceMaster

import json
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from django.db import transaction

@login_required(login_url='login')
def schedule_audit_form_view(request):
    auditors = Official.objects.filter(created_user=request.user)

    addresses = WasteSourceMaster.objects.all().only('id', 'address') #.exclude(source__address_line_1=None)
    locations = MasterSource.objects.all().only('id', 'name')  # Update if you're using address fields directly in Generator

    context = {
        'auditors': auditors,
        'locations': locations,
        'addresses': addresses,
    }
    return render(request, 'audits/schedule-audit-form.html', context)

def send_audit_schedule_email(auditor, location_address, audit_link, company_name, client_name, client_address):
    subject = f"Audit Scheduled ({company_name}, {location_address})"
    to_email = auditor.user.email

    context = {
        "auditor_name": auditor.name,
        "location_address": location_address,
        "audit_link": audit_link,
        "company_name": company_name,
        "client_name": client_name,
        "client_address": client_address,
    }

    # Use async thread
    AsyncEmailSender(
        subject=subject,
        template_name="emails/audit_schedule_email.html",
        context=context,
        to_email=to_email
    ).start()

@require_POST
@login_required
def schedule_audit_submit(request):
    try:
        auditor_id = request.POST.get('auditor')
        scheduled_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        location_ids = request.POST.getlist('audit_location')
        audit_address = request.POST.get('audit_address')
        audit_type = request.POST.get('audit_type')
        note = request.POST.get('note')


        if not all([auditor_id, scheduled_date, end_date, location_ids, audit_address]):
            return JsonResponse({"success": False, "message": "All fields are required."}, status=400)
        
        auditors = Official.objects.get(id=auditor_id)
        audit_address = WasteSourceMaster.objects.get(id=audit_address)

        with transaction.atomic():
            for loc_id in location_ids:
                location = MasterSource.objects.get(id=loc_id)
                audit = Audit.objects.create(
                    officer=auditors,
                    scheduled_date=scheduled_date,
                    end_date=end_date,
                    location=location,
                    destination=audit_address,
                    audit_type=audit_type,
                    note = note
                )

                # Build dynamic audit link
                base_url = request.build_absolute_uri('/')
                audit_link = f"{base_url}audits/audits/add/{audit.id}/"
                address = audit_address.address

                send_audit_schedule_email(
                    auditor=auditors,
                    location_address=address,
                    audit_link=audit_link,
                    company_name=location.name,
                    client_name=request.user.client.company_name if request.user.client else "WasteFlow Admin",
                    client_address=request.user.client.company_address if request.user.client else "N/A"
                )

            

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@login_required(login_url='login')
def get_addresses_by_locations(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        location_ids = data.get('locations', [])

        addresses = list(WasteSourceMaster.objects.filter(
            waste_source__id__in=location_ids
        ).annotate(
            full_address=Concat(
                F('address__address_line_1'), Value(', '),
                F('address__address_line_2'), Value(', '),
                F('address__city'), Value(', '),
                F('address__state'), Value(', '),
                F('address__pin_code'),
                output_field=CharField()
            )
        ).values('id', 'full_address'))
        return JsonResponse({'addresses': addresses})

    return JsonResponse({'error': 'Invalid request'}, status=400)