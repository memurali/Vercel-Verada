import traceback
from django.db import transaction
from abc import ABC, abstractmethod
from django.db import models

# Abstract classes for different responsibilities
class RowProcessor(ABC):
    @abstractmethod
    def process_row(self, row, field_mappings):
        pass

class ForeignKeyResolver(ABC):
    @abstractmethod
    def resolve_foreign_key(self, field, value):
        pass

class BulkInserter(ABC):
    @abstractmethod
    def bulk_insert(self, objects_to_create):
        pass


class GenericRowProcessor(RowProcessor):
    def __init__(self, foreign_key_resolver):
        self.foreign_key_resolver = foreign_key_resolver
        
    def process_row(self, row, field_mappings):
        """
        Processes a row of data by mapping Excel columns to model fields
        and resolving foreign keys.

        :param row: Row of data
        :param field_mappings: Mapping between Excel columns and model fields
        :return: Model data and related data
        """
        model_data = {}
        related_data = {}
        excel_values = row.get("list", {})

        for excel_col, model_field in field_mappings.items():
            value = excel_values.get(excel_col)
            if value is not None:
                if model_field in self.foreign_key_resolver.foreign_keys:
                    instance = self.foreign_key_resolver.resolve_foreign_key(model_field, value)
                    if instance:
                        model_data[model_field] = instance
                        related_data[model_field] = instance
                    else:
                        print(f"[WARNING] ForeignKey '{model_field}' with value '{value}' not found.")
                        model_data[model_field] = None
                        related_data[model_field] = None
                else:
                    model_data[model_field] = value.strip() if isinstance(value, str) else value or None
        return model_data, related_data


class CommodityForeignKeyResolver(ForeignKeyResolver):
    def __init__(self, foreign_keys):
        self.foreign_keys = foreign_keys

    def resolve_foreign_key(self, field, value):
        """
        Resolves the foreign key by fetching the related model instance.
        :param field: The field name (foreign key field)
        :param value: The value to search for in the related model
        :return: The related instance or None if not found
        """
        related_model = self.foreign_keys.get(field)
        if related_model:
            value = value.lower()
            related_instance = related_model.objects.filter(name__iexact=value).first()
            if related_instance:
                return related_instance
            else:
                print(f"Warning: Related instance for '{field}' with value '{value}' not found.")
        return None


class DjangoBulkInserter(BulkInserter):
    def __init__(self, model):
        self.model = model

    def bulk_insert(self, objects_to_create):
        """
        Bulk inserts the objects into the database.

        :param objects_to_create: List of model instances to be inserted.
        """
        with transaction.atomic():
            self.model.objects.bulk_create(objects_to_create)


class GenericBulkUploadService:
    def __init__(self, model, foreign_keys, field_mappings, model_fields, row_processor, foreign_key_resolver, bulk_inserter):
        """
        Initializes the bulk upload service.

        :param model: The model to upload data into.
        :param foreign_keys: A dictionary mapping field names to related models for foreign keys.
        :param field_mappings: A dictionary mapping Excel columns to model fields.
        :param model_fields: List of model fields (used to check if fields are present).
        :param row_processor: An instance of RowProcessor to process rows.
        :param foreign_key_resolver: An instance of ForeignKeyResolver to resolve foreign keys.
        :param bulk_inserter: An instance of BulkInserter to handle bulk insert.
        """
        self.model = model
        self.foreign_keys = foreign_keys
        self.field_mappings = field_mappings
        self.model_fields = model_fields
        self.row_processor = row_processor
        self.foreign_key_resolver = foreign_key_resolver
        self.bulk_inserter = bulk_inserter

    def process_bulk_upload(self, data):
        try:
            rows = data.get("data", [])
            objects_to_create = []
            for row in rows:
                model_data, related_data = self.row_processor.process_row(row, self.field_mappings)
                if not self._is_duplicate(model_data):
                    objects_to_create.append(self.model(**model_data))

            if objects_to_create:
                self.bulk_inserter.bulk_insert(objects_to_create)

            return {"status": "success", "created": len(objects_to_create)}

        except Exception as e:
            return self._handle_error(e)

    def _is_duplicate(self, model_data):
        """
        Checks if a model instance already exists based on the given model data.

        :param model_data: Data to check for duplicates.
        :return: True if a duplicate exists, False otherwise.
        """
        return self.model.objects.filter(**model_data).exists()

    def _handle_error(self, error):
        """
        Handles errors by logging and returning a formatted error response.

        :param error: The exception that occurred.
        :return: A dictionary with the error message.
        """
        error_message = str(error)
        error_traceback = traceback.format_exc()
        print(f"Error occurred: {error_message}")
        print(f"Stack Trace: {error_traceback}")
        return {"status": "error", "message": f"Error: {error_message}\nStack Trace:\n{error_traceback}"}
