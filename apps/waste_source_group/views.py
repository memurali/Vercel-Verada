from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.waste_generators.models import WasteSourceMaster
from apps.waste_source_group.models import MasterSource, WasteGroupMaster, WasteGeneratorGroup
from .services.waste_source_service import WasteSourceService
from apps.common.models import Address


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction

@login_required
def waste_group_master_dashboard(request):
    waste_groups = WasteGroupMaster.objects.select_related('waste_group_generator').all()
    return render(request, "waste_source/waste-group-master-dashboard.html",{
        "waste_groups":waste_groups
    })

@login_required
def waste_group_master_form(request):
    waste_group_generators = WasteGeneratorGroup.objects.all()
    return render(request, "waste_source/waste-group-master-form.html", {
        "waste_group_generators": waste_group_generators
    })

@login_required
def get_group_description(request):
    group_id = request.GET.get("group_id")
    try:
        group = WasteGeneratorGroup.objects.get(id=group_id)
        master = WasteGroupMaster.objects.get(waste_group_generator=group)
        return JsonResponse({"success": True, "description": master.description})
    except WasteGeneratorGroup.DoesNotExist:
        return JsonResponse({"success": False, "message": "Group not found"})
    except WasteGroupMaster.DoesNotExist:
        return JsonResponse({"success": False, "message": "No master entry for this group"})

@require_POST
@transaction.atomic
def submit_waste_group_master(request):
    try:
        source_master_cat = request.POST.get("source_master_cat")

        if source_master_cat == "yes":  # NEW group
            new_group_name = request.POST.get("new_waste_group_name", "").strip()
            description = request.POST.get("description_new", "").strip()

            if not new_group_name or not description:
                return JsonResponse({"success": False, "message": "All fields are required."}, status=400)

            # Create new group generator
            new_group = WasteGeneratorGroup.objects.create(name=new_group_name)

            # Create Waste Group Master
            WasteGroupMaster.objects.create(
                waste_group_generator=new_group,
                threshold=0,
                description=description
            )
        elif source_master_cat == "no":  # EXISTING group
            group_id = request.POST.get("waste_group_id")
            description = request.POST.get("description_exist", "").strip()

            if not group_id or not description:
                return JsonResponse({"success": False, "message": "All fields are required."}, status=400)
            
            try:
                group = WasteGeneratorGroup.objects.get(id=group_id)
                group_master = WasteGroupMaster.objects.get(waste_group_generator=group)
                group_master.description = description
                group_master.save()
                return JsonResponse({"success": True, "message": "Group updated successfully."})
            except WasteGeneratorGroup.DoesNotExist:
                return JsonResponse({"success": False, "message": "Selected group not found."}, status=404)
            except WasteGroupMaster.DoesNotExist:
                return JsonResponse({"success": False, "message": "Group master record does not exist."}, status=404)
        else:
            return JsonResponse({"success": False, "message": "Invalid selection."}, status=400)

        return JsonResponse({"success": True})
    except WasteGeneratorGroup.DoesNotExist:
        return JsonResponse({"success": False, "message": "Selected group does not exist."}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@login_required
def waste_source_master_dashboard(request):
    # waste_source_masters = WasteSourceMaster.objects.select_related('waste_source', 'waste_group').all()
    waste_source_masters = (
        WasteSourceMaster.objects
        .select_related('waste_source', 'waste_group')
        .distinct('waste_source__name')         # DISTINCT ON waste_source.name
    )
    context = {
        "waste_source_masters":waste_source_masters
    }
    return render(request, "waste_source/waste-source-master-dashboard.html", context)

@login_required
def waste_source_master_form(request):
    waste_group_generators = WasteGeneratorGroup.objects.all()
    sources = MasterSource.objects.all().only('id','name')
    context = {
        "waste_group_generators":waste_group_generators,
        "sources":sources
    }
    return render(request, "waste_source/waste-source-master-form.html", context)


@require_POST
def store_waste_source(request):
    try:
        data = request.POST
        WasteSourceService.create_waste_source(data)
        return JsonResponse({"success": True})
    except ValueError as ve:
        return JsonResponse({"success": False, "message": str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": "Internal Server Error"}, status=500)
    


@login_required(login_url='login')
def edit_group_view(request, id):
    waste_group = get_object_or_404(WasteGeneratorGroup, id=id)
    description_entries = WasteGroupMaster.objects.filter(waste_group_generator=waste_group)
    all_groups = WasteGeneratorGroup.objects.all()  # Needed to populate the dropdown

    return render(request, "waste_source/waste-group-edit-form.html", {
        "waste_group": waste_group,  # Assuming you're treating WasteGeneratorGroup like "commodity"
        "description_entries": description_entries,
        "groups": all_groups,
    })



def update_waste_group(request):
    try:
        data = request.POST
        group_id = data.get("id")  # ID of WasteGeneratorGroup to update
        waste_group_id = data.get("waste_group_id")  # Selected group in form
        description_text = data.get("description_exist")

        if not group_id:
            return JsonResponse({"success": False, "message": "Group ID is missing."})

        # Update the WasteGeneratorGroup (if you're allowing changing the name/code, etc.)
        waste_group = get_object_or_404(WasteGeneratorGroup, id=group_id)

        # Update related WasteGroupMaster
        master_entry = WasteGroupMaster.objects.filter(waste_group_generator=waste_group).first()

        if master_entry:
            master_entry.description = description_text
            master_entry.save()
        else:
            # If not found, create new one (optional, depending on your logic)
            WasteGroupMaster.objects.create(
                waste_group_generator=waste_group,
                description=description_text
            )

        return JsonResponse({"success": True, "message": "Waste group master updated successfully."})

    except WasteGeneratorGroup.DoesNotExist:
        return JsonResponse({"success": False, "message": "Waste group not found."})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required(login_url='login')
def edit_group_master_view(request, id):
    source_master = get_object_or_404(WasteSourceMaster, id=id)

    return render(request, "waste_source/waste-source-master-edit-form.html", {
        "source_master": source_master,
        "waste_groups": WasteGeneratorGroup.objects.all(),  # 🔁 list of groups
        "source_name": MasterSource.objects.all(),
        "address_list": Address.objects.all(),
        "status": WasteSourceMaster.objects.filter(status='A'),
    })


# @require_POST
def update_waste_group_master(request):
    try:
        data = request.POST

        # Fetching POST data
        source_id = data.get("id")
        group_id = data.get("waste_group_master")
        generator_id = data.get("generator_id")
        address_id = data.get("address")
        is_active = data.get("active_status")

        if not source_id:
            return JsonResponse({"success": False, "message": "Source ID is missing."})

        # Fetch the source record to update
        source = get_object_or_404(WasteSourceMaster, id=source_id)

        with transaction.atomic():
            # Update group
            if group_id:
                source.waste_group = get_object_or_404(WasteGeneratorGroup, id=group_id)

            # Update generator
            if generator_id:
                source.waste_source = get_object_or_404(MasterSource, id=generator_id)

            # Update address
            if address_id:
                source.address = get_object_or_404(Address, id=address_id)

            # Update status
            source.status = 'A' if is_active == 'on' else 'I'

            # Save the changes
            source.save()

        return JsonResponse({"success": True, "message": "Source Master updated successfully."})

    except WasteSourceMaster.DoesNotExist:
        return JsonResponse({"success": False, "message": "Source Master not found."})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@require_POST
def delete_waste_source_master(request):
    try:
        # Parse the list of waste group IDs from the request body
        waste_source_master_ids = request.POST.getlist("waste_source_master_ids[]")
        
        # Delete the corresponding rows
        WasteGeneratorGroup.objects.filter(id__in=waste_source_master_ids).delete()

        return JsonResponse({"success": True, "message": "Selected rows deleted successfully."})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@require_POST
def delete_waste_group_master(request):
    try:
        # Parse the list of waste group IDs from the request body
        waste_group_master_ids = request.POST.getlist("waste_group_master_ids[]")
        
        # Delete the corresponding rows
        MasterSource.objects.filter(id__in=waste_group_master_ids).delete()

        return JsonResponse({"success": True, "message": "Selected rows deleted successfully."})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
