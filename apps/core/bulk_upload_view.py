import json
import threading
import traceback
from django.http import JsonResponse
from django.db import IntegrityError, transaction
from apps.core.services.bulk_upload_service import GenericBulkUploadService, GenericRowProcessor, CommodityForeignKeyResolver, DjangoBulkInserter
from apps.core.models import CommodityMater, MeasuringUnitMaster, CommodityGroup

class BulkUploadProcessor:
    def __init__(self, model, foreign_keys, field_mappings, model_fields):
        """
        Initializes the bulk upload processor.
        
        :param model: The model to upload data into.
        :param foreign_keys: A dictionary mapping foreign key fields to related models.
        :param field_mappings: A dictionary mapping Excel columns to model fields.
        :param model_fields: List of fields in the target model.
        """
        self.model = model
        self.foreign_keys = foreign_keys
        self.field_mappings = field_mappings
        self.model_fields = model_fields

    def process_bulk_upload(self, data):
        """
        Main method to handle the bulk upload process.
        
        :param data: The bulk data to be processed.
        :return: Result of the bulk upload process.
        """
        try:
            # Extract mappings and rows
            field_mappings = data.get("mappings", {})
            rows = data.get("data", [])
            objects_to_create = []

            foreign_key_resolver = CommodityForeignKeyResolver(self.foreign_keys)

            # Create the bulk upload service instance with required dependencies
            bulk_upload_service = GenericBulkUploadService(
                model=self.model,
                foreign_keys=self.foreign_keys,
                field_mappings=self.field_mappings,
                model_fields=self.model_fields,
                row_processor=GenericRowProcessor(foreign_key_resolver),
                foreign_key_resolver=foreign_key_resolver,
                bulk_inserter=DjangoBulkInserter(self.model)
            )

            # Process each row and prepare data
            for row in rows:
                # Corrected method call to `process_row` instead of `process_row_data`
                model_data, related_data = bulk_upload_service.row_processor.process_row(row, self.field_mappings)
                
                if not bulk_upload_service._is_duplicate(model_data):
                    objects_to_create.append(self.model(**model_data))

            # Bulk insert objects into the database
            if objects_to_create:
                self._bulk_insert(objects_to_create)

            return {"status": "success", "created": len(objects_to_create)}

        except Exception as e:
            return self._handle_error(e)

    def _bulk_insert(self, objects_to_create):
        """
        Performs the bulk insert into the database within a transaction.
        
        :param objects_to_create: List of model instances to be inserted.
        """
        try:
            with transaction.atomic():  # Ensure atomicity for the insert
                self.model.objects.bulk_create(objects_to_create)
        except IntegrityError as e:
            print(f"Integrity error during bulk insert: {str(e)}")
            raise

    def _handle_error(self, error):
        """
        Handles errors during the bulk upload process and logs the details.
        
        :param error: The error encountered during processing.
        :return: A response dictionary with the error message and stack trace.
        """
        error_message = str(error)
        error_traceback = traceback.format_exc()
        return {"status": "error", "message": f"Error: {error_message}\nStack Trace:\n{error_traceback}"}
    

class BulkUploadPreValidator:
    def __init__(self, data):
        self.data = data.get("data", [])
        self.mappings = data.get("mappings", {})
        print(f"self.mappings: {self.mappings}")
        self.errors = []

        # Load valid options from DB
        self.valid_units = set(map(str.lower, MeasuringUnitMaster.objects.values_list("name", flat=True)))
        self.valid_groups = set(CommodityGroup.objects.values_list("code", flat=True))
        self.valid_statuses = {"A", "I"}

    def validate(self):
        for idx, row in enumerate(self.data, start=1):
            values = row.get("list", {})

            # Fetch mapped fields
            unit_field = self.mappings.get("measuring_unit")
            group_field = self.mappings.get("group") or self.mappings.get("Commodity Group")
            status_field = self.mappings.get("Status")

            # Get actual values
            unit_value = values.get(unit_field).lower()
            group_value = values.get(group_field).lower()
            status_value = values.get(status_field)

            # Perform validations
            if unit_value and unit_value not in self.valid_units:
                self.errors.append(f"Row {idx}: Invalid measuring_unit '{unit_value}'")

            if group_value and group_value not in self.valid_groups:
                self.errors.append(f"Row {idx}: Invalid group '{group_value}'")

            if status_value and status_value not in self.valid_statuses:
                self.errors.append(f"Row {idx}: Invalid status '{status_value}' (must be 'A' or 'I')")

        return self.errors


def start_bulk_upload_thread(data):
    """
    Starts the bulk upload process in a separate thread.
    
    :param data: The data to be processed for the bulk upload.
    """
    try:
        # Instantiate the processor with required dependencies
        processor = BulkUploadProcessor(
            model=CommodityMater,
            foreign_keys={
                "measuring_unit": MeasuringUnitMaster,
                "group": CommodityGroup,
            },
            field_mappings=data.get("mappings", {}),
            model_fields=[field.name for field in CommodityMater._meta.fields if field.name != "id"]
        )

        result = processor.process_bulk_upload(data)
        print(result)  # Optionally log or store the result

    except Exception as e:
        print(f"Error processing bulk upload: {str(e)}")

def bulk_upload_commodity_data(request):
    """
    API endpoint to trigger the bulk upload process in a background thread.
    
    :param request: The incoming HTTP request containing the data to be uploaded.
    :return: JSON response with the status of the operation.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request"}, status=400)
    
    try:
        data = json.loads(request.body)

        validator = BulkUploadPreValidator(data)
        errors = validator.validate()

        print(f"errors: {errors}")

        if errors:
            return JsonResponse({"status": "error", "errors": errors}, status=422)
        
        # Start the bulk upload process in a background thread
        thread = threading.Thread(target=start_bulk_upload_thread, args=(data,))
        thread.start()

        # Respond immediately to the client
        return JsonResponse({"status": "success", "message": "Bulk upload started in the background."})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


