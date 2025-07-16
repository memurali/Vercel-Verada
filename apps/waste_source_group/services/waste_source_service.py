from django.core.exceptions import ObjectDoesNotExist
from apps.common.models import Address
from apps.waste_generators.models import WasteSourceMaster
from apps.waste_source_group.models import MasterSource, WasteGeneratorGroup

class WasteSourceService:

    @staticmethod
    def create_waste_source(data):
        source_type = data.get("source_type")
        group_id = data.get("waste_group_master")
        description = data.get("Desciption")
        status = 'A' if data.get("Staus") == 'yes' else 'I'

        contact_name = data.get("contact_name")
        contact_phone = data.get("contact_phone")
        contact_email = data.get("contact_email")

        if not group_id:
            raise ValueError("Waste group is required")

        try:
            group = WasteGeneratorGroup.objects.get(id=group_id)
        except WasteGeneratorGroup.DoesNotExist:
            raise ValueError("Invalid waste group ID")

        if source_type == "yes":
            source_name = data.get("new_source_name")
            if not source_name:
                raise ValueError("Source name is required")
            master_source = MasterSource.objects.create(name=source_name)
        else:
            source_id = data.get("existing_source_id")
            try:
                master_source = MasterSource.objects.get(id=source_id)
            except MasterSource.DoesNotExist:
                raise ValueError("Invalid source ID")

        address = Address.objects.create(
            address_line_1=data.get('address_one'),
            address_line_2=data.get('address_two'),
            city=data.get('city'),
            state=data.get('state'),
            pin_code=data.get('zipcode'),
        )

        WasteSourceMaster.objects.create(
            waste_source=master_source,
            status=status,
            waste_group=group,
            address=address,
            description=description,
            contact_name=contact_name,
            contact_phone=contact_phone,
            contact_email=contact_email
        )
