from django.db.models import Q
from django.http import JsonResponse
from apps.waste_generators.models import Generator, WasteSourceMaster, WasteSourceSpecificationMaster
from apps.waste_source_group.models import WasteGroupMaster, WasteGeneratorGroup
from django.db import transaction
from apps.users.models import User

class GeneratorService:

    @staticmethod
    def search_generators(query):
        qs = Generator.objects.select_related(
            "Waste_generator_group", "waste_source_specification", "user"
        )
        if query:
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(address_line_1__icontains=query) |
                Q(contact_name__icontains=query) |
                Q(contact_email__icontains=query)
            )
        return qs.order_by("id")
    
    @staticmethod
    @transaction.atomic
    def save_generator(request):
        try:
            data = request.POST
            group = WasteGeneratorGroup.objects.get(id=data["waste_group"])
            specification = WasteSourceSpecificationMaster.objects.get(id=data["specification"])

            # Replace this logic with actual user creation
            user = User.objects.first()

            Generator.objects.create(
                user=user,
                name=data["waste_generator_name"],
                address=f"{data['address_one']} {data['address_two']}",
                city=data["city"],
                pin_code=data["zipcode"],
                waste_source=group.wastesourcemaster_set.first(),
                waste_source_specification=specification
            )

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    
    @staticmethod
    @transaction.atomic
    def handle_submission(request):
        try:
            data = request.POST
            generator_id = data.get("id")
            is_edit = bool(generator_id)

            waste_generator_group_obj = WasteGeneratorGroup.objects.get(id=data.get("waste_group"))

            if is_edit:
                generator = Generator.objects.select_related('user').get(id=generator_id)
                generator.name = data.get("waste_generator_name")
                generator.address_line_1 = data.get("address_one", '')
                generator.address_line_2 = data.get("address_one", '')
                generator.city = data.get("city")
                generator.state = data.get("state")
                generator.pin_code = data.get("zipcode")
                generator.Waste_generator_group = waste_generator_group_obj
                generator.contact_name = data.get("contact_name")
                generator.contact_phone = data.get("contact_phone")
                generator.contact_email = data.get("contact_email")
                generator.is_active = data.get("waste_generator_status") == "on"
                generator.save()
                return JsonResponse({"success": True, "message": "Generator updated successfully!"})
            else:
                Generator.objects.create(
                    user=request.user,
                    name=data.get("waste_generator_name"),
                    address_line_1 = data.get("address_one", ''),
                    address_line_2 = data.get("address_one", ''),
                    city=data.get("city"),
                    state = data.get("state"),
                    pin_code=data.get("zipcode"),
                    Waste_generator_group=waste_generator_group_obj,
                    contact_name = data.get("contact_name"),
                    contact_phone = data.get("contact_phone"),
                    contact_email = data.get("contact_email"),
                    is_active = data.get("waste_generator_status") == "on"
                )
                return JsonResponse({"success": True, "message": "Generator added successfully!"})

        except Exception as e:
            print(f"e: {e}")
            return JsonResponse({"success": False, "message": str(e)})

