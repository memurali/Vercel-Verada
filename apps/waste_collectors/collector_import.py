from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from apps.waste_generators.models import WastePickUp, WasteSource, WasteSourceMaster
from apps.waste_source_group.models import MasterSource
from apps.core.models import CommodityGroup, MeasuringUnitMaster
from apps.common.models import Address
from decimal import Decimal
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from apps.waste_collectors.models import Collector, CollectorType
from django.db import transaction, models, connection
from apps.core.models import CommodityMater
from django.views.decorators.csrf import csrf_exempt
import pandas as pd, json, openpyxl
from django.http import JsonResponse, HttpResponse
from apps.waste_collectors.models import Collector
from datetime import datetime, timedelta, date
from django.apps import apps


# Import 
@login_required(login_url='login')
def waste_collector_import(request):
    return render(request, "collectors/waste-collector-import-form.html")

def waste_collector_download_template(request):
    collector_types = CollectorType.objects.all()
    return render(request, "collectors/waste-collector-download_template.html", {
        "collector_types": collector_types
    })

# Import 
def get_common_model_classes():
    return [
        Collector,
        CollectorType,
        Address,
    ]


def upload_get_model_columns(model):
    app_name = model._meta.app_label
    model_name = model.__name__.lower()  # or model._meta.model_name
    prefix_column_name = {
        field.name: f"{app_name}-{model_name}-{field.name}"
        for field in model._meta.fields
    }
    return prefix_column_name
  

def upload_getting_model_names():
    model_classes = get_common_model_classes()

    all_fields = {
        model.__name__: upload_get_model_columns(model)
        for model in model_classes
    }

    model_names_list = [
        all_fields.get('Collector', {}).get('name'),
        all_fields.get('CollectorType', {}).get('name'),
        all_fields.get('Collector', {}).get('collector_create_date'),
        all_fields.get('Address', {}).get('address_line_1'),
        all_fields.get('Collector', {}).get('tax_id'),
    ]

    return model_names_list


@csrf_exempt
def upload_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        excel_file = request.FILES['file']
        df = pd.read_excel(excel_file)

        # Step 1: Extract headers from uploaded Excel
        file_columns = list(df.columns)

        model_fields = upload_getting_model_names()

        # Convert DataFrame rows to a list of dicts
        data_rows = []
        for _, row in df.iterrows():
            data_rows.append({"list": row.to_dict()})


        # Step 4: Prepare the JSON response
        response_data = {
            "localization": {},
                "options": {
                    "associationMode": "oneToOne", # oneToOne,manyToMany
                    "lineStyle": "square-ends",
                    "buttonErase": "Erase Links",
                    "displayMode": "original",
                    # "whiteSpace": $("input[name='whiteSpace']:checked").val(),
                    "mobileClickIt": False
                },
            "Lists": [
                {
                    "name": "Columns in files",
                    "list": file_columns
                },
                {
                    "name": "Available Fields",
                    "list": model_fields,
                    # "mandatories": mandatory_fields
                }
            ],
            "data": data_rows  # ✅ This is important!
        }

        return JsonResponse(response_data)
    
    return JsonResponse({"error": "Invalid request"}, status=400)


def map_get_model_with_prefix(model_class):
    return [
        f'{model_class._meta.app_label}.{model_class._meta.model_name}.{field.name}' 
        for field in model_class._meta.get_fields()
        if isinstance(field, models.Field)
    ]


def map_getting_model_fields_names():
    model_classes = get_common_model_classes()

    model_names = []
    for model_class in model_classes:
        model_names.extend(map_get_model_with_prefix(model_class))
    
    return model_names


def get_specific_model_map():
    model_classes = get_common_model_classes()
    
    model_map = {}
    for model in model_classes:
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        model_map[(app_label, model_name)] = model
        
    return model_map


def update_record_with_unique_ids(temp_models, model_map):
    """
    Update string values in temp_models with corresponding object IDs
    based on model_map, except for models that should be left as-is.
    """
    # Define models to skip (do not replace strings with IDs)
    skip_id_lookup_keys = {('common', 'address')}

    for key, records in temp_models.items():
        if key in skip_id_lookup_keys:
            continue  # Skip this model

        model_class = model_map.get(key)
        if not model_class:
            # print(f"[SKIP] No model found for key: {key}")
            continue

        for record in records:
            for field, value in record.items():
                if isinstance(value, str):
                    try:
                        # obj = model_class.objects.get(**{field: value})
                        obj = model_class.objects.get(**{f"{field}__iexact": value.lower()})
                        record[field] = obj.id
                    except model_class.DoesNotExist:
                        print(f"[NOT FOUND] {model_class.__name__}: No match for {field}='{value}'")
                    except model_class.MultipleObjectsReturned:
                        print(f"[WARNING] Multiple matches for {field}='{value}' in {model_class.__name__}")

    return temp_models


def remove_new_items(temp_models, model_map):
    # Only focusing on 'collectortype' foreign key for now
    fk_required_keys = {
        ('waste_collectors', 'collectortype'),
    }

    total_records = len(next(iter(temp_models.values())))
    valid_indexes = set(range(total_records))

    for key in fk_required_keys:
        model_class = model_map.get(key)

        if not model_class:
            print(f"Model class not found for {key}, skipping all rows.")
            valid_indexes = set()
            break

        current_valid_indexes = set()
        records = temp_models.get(key, [])

        for i, record in enumerate(records):
            is_valid = True

            for field, value in record.items():
                if isinstance(value, str):  # Case-insensitive string lookup for 'name'
                    try:
                        # Perform a case-insensitive lookup for the 'name' field in 'collectortype'
                        obj = model_class.objects.get(**{f"{field}__iexact": value.lower()})
                    except model_class.DoesNotExist:
                        is_valid = False  # If no matching name, skip this record
                        break
                else:
                    # Skip non-foreign key fields
                    continue

            if is_valid:
                current_valid_indexes.add(i)

        valid_indexes &= current_valid_indexes

    # Now, return the cleaned models, only including the valid indexes for 'collectortype'
    cleaned_models = {}
    for key, records in temp_models.items():
        if key == ('waste_collectors', 'collectortype'):
            # Only include valid rows from the 'collectortype' model
            cleaned_models[key] = [records[i] for i in sorted(valid_indexes)]
        else:
            # Skip foreign key checks for other keys
            cleaned_models[key] = records

    return cleaned_models


@csrf_exempt
def save_mapped_data(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        mappings = data.get("mappings", {})
        rows = data.get("data", [])

        # label lookup: column name -> (app, model, field)
        model_fields = map_getting_model_fields_names()

        label_lookup = {}

        for path in model_fields:
            parts = path.split(".")
            if len(parts) == 3:
                app_label, model_name, field_label = map(str.strip, parts)

                if field_label not in label_lookup:
                    label_lookup[field_label] = []
                label_lookup[field_label].append((app_label, model_name, field_label))

        # Grouping by (app_label, model_name) => list of model instances
        model_data_map = {}

        for row in rows:
            excel_values = row.get("list", {})

            # Temporary dictionary to hold data for a single row
            temp_models = {}  # (app_label, model_name) => field dictionary

            for excel_col, mapp_field in mappings.items():
                map_app_name, table_name_field, mapped_field = mapp_field.split('-')  # e.g. 'wastesource-waste_weight'
                value = excel_values.get(excel_col, None)

                if isinstance(value, str):
                    value = value.strip()

                # Check if field exists in lookup
                if mapped_field in label_lookup:
                    for app_label, model_name, field_name in label_lookup[mapped_field]:
                         if model_name == table_name_field and app_label == map_app_name:
                            model_key = (app_label, model_name)
                            if model_key not in temp_models:
                                temp_models[model_key] = {}
                            temp_models[model_key][field_name] = value
                            break  # match found, skip further loop
            
            # Parse the values for each field dynamically
            # print(temp_models,">>>>>>>>>>>")
            for model_key, field_data in temp_models.items():
                app_label, model_name = model_key
                model_class = apps.get_model(app_label, model_name)

                for field_name, value in field_data.items():
                    field_obj = model_class._meta.get_field(field_name)
                    parsed_value = datatype_field_value(field_obj, value)
                    field_data[field_name] = parsed_value
                # Handle foreign key fields like waste_source_id
                model_data_map.setdefault(model_key, []).append(field_data)

        # Example Usage:
        model_map = get_specific_model_map()
        # print(model_data_map,model_map,"................")
        removed_new_items = remove_new_items(model_data_map, model_map)
        # print(removed_new_items,"..............")
        updated_records = update_record_with_unique_ids(removed_new_items, model_map)
        
        # Get raw data lists
        # Loop through each index
        collected_values = {}

        # print(updated_records,".............")

        for (app_label, model_name), records in updated_records.items():
            key = model_name
            
            if model_name == 'address':
                values = [record.get('address_line_1') for record in records if 'address_line_1' in record]
                collected_values[key] = {'name': values}

            else:
                collected_values[key] = {}
                for field in ['name', 'tax_id', 'collector_create_date']:
                    field_values = [record.get(field) for record in records if field in record]
                    if field_values:
                        collected_values[key][field] = field_values

        # Extract values
        # print(collected_values,"...............")
        collectorname = collected_values.get('collector', {}).get('name', [])
        collector_type_id = collected_values.get('collectortype', {}).get('name', [])
        tax_ids = collected_values.get('collector', {}).get('tax_id', [])
        pickupdate = collected_values.get('collector', {}).get('collector_create_date', [])
        address_names = collected_values.get('address', {}).get('name', [])
        # print(address_names,">>>>>>>>>>>>>")

        record_count = min(len(collectorname), len(pickupdate), len(tax_ids), len(address_names), len(collector_type_id))
        
        # Create WasteSource and WastePickUp objects
        new_data_added = False  # Track if we create any new records


        for i in range(record_count):
            # Get values for this iteration
            pickup_date = str(pickupdate[i])
            collector_name = collectorname[i]
            collector_type_ids = collector_type_id[i]
            address_namess = address_names[i]
            tax_id = tax_ids[i]
            collector_create_date = date.fromisoformat(pickup_date)

            # Check if the address already exists
            cursor = connection.cursor()

            address_parts = address_namess.split(',')
            if len(address_parts) < 4:
                print(f"⚠️ Skipping row {i} due to incomplete address: {address_namess}")
                continue  # Skip if 

            
            address_line_1 = address_parts[0].strip()
            city = address_parts[1].strip()
            state = address_parts[2].strip()
            pin_code = address_parts[3].strip()
          
            cursor.execute(f"SELECT id, address_line_1 FROM common_address where address_line_1 in ('{address_line_1}') ")
            existing_record = cursor.fetchall()



            if len(existing_record) != 0:
                # return JsonResponse({'status': 'error', 'message': 'Address already exists'})
                address_id = existing_record[0][0]
                print(address_id,">>>>>>>>>>>")
                collector_address = Address.objects.get(id=address_id)
                print(collector_address,"LLLLLLLLLLL")

            else:
                collector_address, _ = Address.objects.get_or_create(
                address_line_1=address_line_1,
                address_line_2="",
                city=city,
                state=state,
                pin_code=pin_code,
            )

            print(collector_address,"...............")
           
            Collector.objects.get_or_create(
                user_id=1,
                name=collector_name,
                tax_id=tax_id,
                collector_type_id=collector_type_ids,
                collector_create_date=collector_create_date,
                address=collector_address,  # 👈 Use instance, not ID
                is_active=True,
            )

            new_data_added = True  # At least one record added

        # Final check
        if not new_data_added:
            return JsonResponse({'message': 'There is No Unique Data'})

        return JsonResponse({"status": "success"})


    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)



def datatype_field_value(field, value):
    """Parse the value according to the model field type."""


    if isinstance(field, models.DateTimeField):
        if isinstance(value, (int, float)):
            return datetime(1899, 12, 30) + timedelta(days=int(value))
        elif isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return None
        return None

    elif isinstance(field, models.DateField):
        if value in [None, "", "NA"]:
            return None
        if isinstance(value, (int, float)):
            return (datetime(1899, 12, 30) + timedelta(days=int(value))).date()
        elif isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                return None
        return None

    elif isinstance(field, models.IntegerField):
        try:
            return int(value) if value not in [None, "", "NA"] else None
        except (ValueError, TypeError):
            return None

    elif isinstance(field, models.FloatField):
        try:
            return float(value) if value not in [None, "", "NA"] else None
        except (ValueError, TypeError):
            return None

    elif isinstance(field, models.CharField):
        return value if value not in [None, ""] else "NA"

    elif isinstance(field, models.BooleanField):
        return str(value).lower() in ["true", "1"]

    elif isinstance(field, models.ForeignKey):
        related_model = field.related_model
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
            fk_id = int(value)
            try:
                return related_model.objects.get(id=fk_id)
            except related_model.DoesNotExist:
                return None
        return None



def download_template(request):
    collector_type = request.GET.get("collector_type", "N/A")

    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Template"

    # Define only the needed fields as headers
    headers = [
        "Adddress",    # Possibly from CommodityMater.name or another related model
        "Collector Date",
        "Collector Name",         # Assuming from WastePickUp or related Collector
        "Tax Number",      # You may need to concatenate address_line_1 and address_line_2
        "Collector Type",   # Custom label for something like WastePickUp.waste_source
    ]


    # Add headers to Excel
    ws.append(headers)

    # Create one blank row with generator & location filled
    row = [""] * len(headers)
    try:
        Collector_index = headers.index("Collector Type")
        row[Collector_index] = collector_type
    except ValueError:
        pass


    ws.append(row)

    # Return response
    filename = f"template_{collector_type}.xlsx".replace(" ", "_")
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}'
    wb.save(response)
    return response

