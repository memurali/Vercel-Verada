from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.utils.timezone import now
import json
from django.core.serializers.json import DjangoJSONEncoder
from apps.audits.models import Audit, AuditCommoditi 
from apps.agreements.models import AgreementItem
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def audit_report_view(request, audit_id):
    audit = get_object_or_404(Audit, id=audit_id)
    commodity_data = (
        AuditCommoditi.objects
        .filter(audit=audit)
        .values('commodity_group__name', 'image')
        .annotate(total_weight=Sum('weight'), toal_contamination_weight=Sum('contamination_weight'))
    )

    total_weight = sum(item['total_weight'] or 0 for item in commodity_data) or 1  # Avoid division by zero
    toal_contamination_weight = sum(item['toal_contamination_weight'] or 0 for item in commodity_data) or 1  # Avoid division by zero

    table_data = []
    chart_data = []

    base_url = request.build_absolute_uri('/')
    total_percent = 0
    for item in commodity_data:
        name = item['commodity_group__name']
        weight = int(item['total_weight'])
        contamination_weight = int(item['toal_contamination_weight'])
        percent = round(((weight - contamination_weight) / int(total_weight)) * 100, 2)
        images = f"{base_url}media/{item.get('image')}"
        total_percent += percent

        print(f"percent: {percent}")

        table_data.append({
            "name": name,
            "weight": weight,
            "contamination_weight": contamination_weight,
            "percent": f"{round(percent,2)}%",
            "images": images
        })

        if audit.audit_type == "verification":
            chart_data.append([name, weight-contamination_weight])
        else:
            chart_data.append([name, weight])

    if audit.audit_type == "verification":
        chart_data.append(['Contamination Weight', toal_contamination_weight])

    # Add total row
    table_data.append({
        "name": "Total",
        "weight": total_weight,
        "contamination_weight": toal_contamination_weight,
        "percent": f"{round(total_percent,2)}%",
        "images": []
    })

    context = {
        "company_name": "XYZ",
        "company_display_name": audit.location.name,
        "company_email": "XYZ@gmail.com",
        "company_phone": '23454345646',  # Replace if stored somewhere
        "company_website": "www.gearthinc.com",
        "audit_date": audit.scheduled_date.strftime("%m/%d/%Y"),
        "audit_type": audit.audit_type.title(),  # Initial / Verification
        "diversion_percentage": total_percent,  # or calculate using commodity types
        "chart_title": "Diversion Statistics",
        "table_data": table_data,
        "chartdata_json": json.dumps(chart_data, cls=DjangoJSONEncoder),
    }

    return render(request, "audits/report-audit.html", context)
