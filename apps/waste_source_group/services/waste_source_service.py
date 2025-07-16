from django.core.exceptions import ObjectDoesNotExist
from apps.common.models import Address
from apps.waste_generators.models import WasteSourceMaster
from apps.waste_source_group.models import MasterSource, WasteGeneratorGroup
from apps.common.models import tbl_ErrorLog as ErrorLog  # replace 'your_app' with your actual app name
from django.http import JsonResponse

import traceback
import sys

class WasteSourceService:

    @staticmethod
    def create_waste_source(data):
        try:
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
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_list = traceback.extract_tb(exc_traceback)
            
            # Get the last traceback item (where the exception occurred)
            filename, line_number, function_name, text = tb_list[-1]
            
            # Log to database
            ErrorLog.objects.create(
                error_message=str(e),
                file_name=filename,
                line_number=line_number,
                function_name=function_name,
                error_line=text
            )
            
            # Optionally print or log elsewhere
            print(f"Exception on line {line_number} in {filename}: {e}")

            return JsonResponse({'message': 'There is No Unique Data'}, status=400)
