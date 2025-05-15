from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from apps.audits.models import AuditLocation, Audit,  AuditCommoditi, AuditCompliance
from apps.core.models import CommodityGroup
from decimal import Decimal
from apps.waste_source_group.models import MasterSource
from django.db import transaction

@login_required(login_url='login')
def audit_form_view(request, audit_id):
    audit = get_object_or_404(Audit, id=audit_id)

    groups = CommodityGroup.objects.all()

    commodities = audit.audit_commoditi.all()
    compliance = audit.audit_compliance.first()

    address = audit.destination.address
    weights = {ac.commodity_group.code.lower(): ac.weight for ac in commodities}
    contamination_weights = {ac.commodity_group.code.lower(): ac.contamination_weight for ac in commodities}
    selected_commodities = [ac.commodity_group.code.lower() for ac in commodities]

    contaminant = {
        'fw': audit.media.find('fw') != -1,
        'recycle': audit.media.find('recycle') != -1,
        'landfill': audit.media.find('landfill') != -1,
    }

    locations = MasterSource.objects.all().only('id', 'name') 

    context = {
        'audit': audit,
        'groups': groups,
        'weights': weights,
        'selected_commodities': selected_commodities,
        'compliance': compliance.compliance if compliance else False,
        'contaminant': contaminant,
        'locations': locations,
        'address': address,
        'contamination_weights': contamination_weights
    }
    return render(request, "audits/audit-form.html", context)

@require_POST
@login_required(login_url='login')
def audit_form_submit(request):
    try:
        audit_id = request.POST.get("audit_id")
        location_id = request.POST.get("location")
        audit_type = request.POST.get("audit_type")  # 'initial' or 'verification'
        compliance = request.POST.get("compliance")
        scheduled_date = request.POST.get("scheduled_date")
        note = request.POST.get('note')
        is_waiver_applied = request.POST.get('is_waiver_applied') == 'on'
        waiver_type = request.POST.get('waiver_type')

        audit = Audit.objects.get(id=audit_id)

        location_obj = MasterSource.objects.get(id=location_id)
        audit.location = location_obj
        audit.audit_type = audit_type
        audit.scheduled_date = scheduled_date
        audit.note = note
        audit.status = 'C'
        audit.is_waiver_applied = is_waiver_applied
        audit.waiver_type = waiver_type

        audit.audit_commoditi.all().delete()
        audit.audit_compliance.all().delete()
        audit.save()

        # If waiver is applied, skip adding commodities and compliance
        if is_waiver_applied:
            return JsonResponse({"success": True})

        groups = CommodityGroup.objects.all()
        with transaction.atomic():
            for group in groups:
                code = group.name.lower().strip().replace(" ", "_")
                weight_field = f"{audit_type}_total_weight_{code}"
                contamination_weight_field = f"{audit_type}_contamination_weight_{code}"
                image_field = f"{audit_type}_audit_picture_{code}"


                weight_val = request.POST.get(weight_field)
                contamination_weight_val = request.POST.get(contamination_weight_field)
                weight = Decimal(weight_val) if weight_val else Decimal("0.00")
                contamination_weight = Decimal(contamination_weight_val) if contamination_weight_val else Decimal("0.00")
                image = request.FILES.get(image_field)

                if weight > 0 or image:
                    AuditCommoditi.objects.create(
                        audit=audit,
                        commodity_group=group,
                        weight=weight,
                        contamination_weight=contamination_weight,
                        image=image,
                        contaminant_found=False
                    )

            # Save compliance if audit is verification
            if audit_type == "verification":
                AuditCompliance.objects.create(
                    audit=audit,
                    compliance=(compliance == "yes")
                )


        return JsonResponse({"success": True})
    except Audit.DoesNotExist:
        return JsonResponse({"success": False, "message": "Audit not found."}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
