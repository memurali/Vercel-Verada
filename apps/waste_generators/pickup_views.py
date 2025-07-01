from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from apps.waste_generators.models import WastePickUp, WasteSource, WasteSourceMaster
from apps.waste_source_group.models import MasterSource
from apps.core.models import CommodityGroup, MeasuringUnitMaster, CommodityMater
from apps.common.models import Address
from decimal import Decimal
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from apps.waste_collectors.models import Collector, CollectorType
from django.db import transaction, models, connection
from django.views.decorators.csrf import csrf_exempt
import pandas as pd, json, openpyxl
from django.http import JsonResponse, HttpResponse
from apps.waste_collectors.models import Collector
from datetime import datetime, timedelta
from django.apps import apps
from django.conf import settings
from s3 import upload_file_to_s3_fileobj


@login_required(login_url='login')
def waste_pickup_dashboard(request):
    search_query = request.GET.get('q', '').strip()

    pickups = WastePickUp.objects.select_related(
        'waste_source__waste_source',
        'waste_source__food_type',
        'waste_source__waste_type',
        'destination'
    )

    if search_query:
        pickups = pickups.filter(
            Q(waste_source__waste_source__name__icontains=search_query) |
            Q(waste_source__food_type__name__icontains=search_query) |
            Q(waste_source__waste_type__name__icontains=search_query) |
            Q(destination__name__icontains=search_query)
        )

    pickups = pickups.order_by('-id')

    return render(request, 'pickups/pickup_dashboard.html', {
        'pickups': pickups,
        'search_query': search_query
    })


@login_required(login_url='login')
def waste_pickup_form_view(request):
    context = {
        "sources": MasterSource.objects.all(),
        "waste_types": CommodityGroup.objects.all(),
        "destinations": Collector.objects.all(),
        "food_type": CommodityMater.objects.all()
    }
    return render(request, "pickups/waste-Pickups-form.html", context)


def get_pickup_food_type(request, group_id):
    commodities = list(CommodityMater.objects.filter(group_id=group_id, created_user=request.user).values('id', 'name'))
    return JsonResponse({'commodities': commodities})


@require_POST
@transaction.atomic
def submit_waste_pickup(request):
    try:
        source = MasterSource.objects.get(id=request.POST.get("generator"))
        waste_type = CommodityGroup.objects.get(id=request.POST.get("waste_type"))
        food_type = CommodityMater.objects.get(id=request.POST.get("food_type"))
        destination = Collector.objects.get(id=request.POST.get("destination"))
        waste_weight = Decimal(request.POST.get("waste_weight"))
        pickup_date = request.POST.get("pikcup_date")
        address =  WasteSourceMaster.objects.get(id=request.POST.get("address"))
        image = request.FILES.get("upload_file")
        image = upload_file_to_s3_fileobj(image, 'Pickup')

        waste_source = WasteSource.objects.create(
            waste_source=source,
            waste_type=waste_type,
            food_type=food_type,
            waste_weight=waste_weight
        )

        WastePickUp.objects.create(
            pickup_date=pickup_date,
            waste_source=waste_source,
            address=address.address,
            image=image,
            destination=destination
        )

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})



@login_required(login_url='login')
def edit_pickup_view(request, pickup_id):
    pickup = get_object_or_404(WastePickUp, id=pickup_id)

    return render(request, "pickups/waste-pickup-edit-form.html", {
        "pickup": pickup,
        "waste_source_list": MasterSource.objects.all(),
        "waste_type_list": CommodityGroup.objects.all(),
        "food_type_list": CommodityMater.objects.all(),
        "address_list": Address.objects.all(),
        "destination_list": Collector.objects.all(),
    })


@require_POST
def update_pickup(request):
    try:
        data = request.POST
        pickup_id = data.get("pickup_id")
        pickup_date = data.get("pickup_date")
        waste_type_id = data.get("waste_type")
        generator_id = data.get("generator_name")
        address = data.get("address")
        food_type_id = data.get("food_type")
        waste_weight = data.get("waste_weight")
        destination_id = data.get("destination")
        upload_file = request.FILES.get("upload_file")

        if not pickup_id:
            return JsonResponse({"success": False, "message": "pickup_id is missing."})

        pickup = WastePickUp.objects.get(id=pickup_id)

        # Convert and update fields
        if pickup_date:
            pickup.pickup_date = datetime.strptime(pickup_date, "%Y-%m-%d").date()

        pickup.address = address

        waste_source = pickup.waste_source
        waste_source.waste_source = MasterSource.objects.get(id=generator_id)
        waste_source.waste_type = CommodityGroup.objects.get(id=waste_type_id)
        waste_source.food_type = CommodityMater.objects.get(id=food_type_id)
        waste_source.waste_weight = float(waste_weight)
        waste_source.save()

        pickup.destination = Collector.objects.get(id=destination_id)

        if upload_file:
            pickup.image = upload_file

        pickup.save()

        return JsonResponse({"success": True, "message": "Pickup updated successfully."})

    except WastePickUp.DoesNotExist:
        return JsonResponse({"success": False, "message": "Pickup not found."})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


# Import 
@login_required(login_url='login')
def waste_Pickups_import(request):
    return render(request, "pickups/waste-pickup-import-form.html")

def waste_Pickups_download_template(request):
    context = {
        "sources": MasterSource.objects.all(),
    }
    return render(request, "pickups/waste-pickup-download_template.html", context)


# Import 
def get_common_model_classes():
    return [
        WastePickUp,
        MasterSource,
        CommodityMater,
        CommodityGroup,
        Collector,
        WasteSource,
        Address,
        CollectorType,
        MeasuringUnitMaster,
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
        all_fields.get('WastePickUp', {}).get('pickup_date'),
        all_fields.get('MasterSource', {}).get('name'),
        all_fields.get('Address', {}).get('address_line_1'),
        all_fields.get('CommodityGroup', {}).get('name'),
        all_fields.get('CommodityMater', {}).get('name'),
        all_fields.get('WasteSource', {}).get('waste_weight'),
        all_fields.get('Collector', {}).get('name')
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
    # Iterate over the temp_models dictionary
    for key, records in temp_models.items():
        # Fetch the model class corresponding to the key (tuple of app_label and model_name)
        model_class = model_map.get(key)
        
        if not model_class:
            # print(f"No model found for key: {key}, skipping...")
            continue  # Skip if the model is not found in the map

        # Process each record for the model
        for record in records:
            # For each field-value pair in the record
            for field, value in record.items():
                if isinstance(value, str):  # Check if the value is a string
                    try:
                        # Try to find the object with the field and its corresponding value (case-insensitive)
                        obj = model_class.objects.get(**{f"{field}__iexact": value.lower()})
                        # If found, update the record with the object's ID
                        record[field] = obj.id
                    except model_class.DoesNotExist:
                        # If the object is not found, log the issue
                        print(f"No match found for {field} = {value} in {model_class.__name__}")
                else:
                    # Handle other value types (optional)
                    continue

    return temp_models  # Return the updated records with IDs



def remove_new_items(temp_models, model_map):
    fk_required_keys = {
        ('common', 'address'),
        ('core', 'commoditygroup'),
        ('core', 'commoditymater'),
    }

    total_records = len(next(iter(temp_models.values())))
    valid_indexes = set(range(total_records))

    for key in fk_required_keys:
        model_class = model_map.get(key)
        # print(f"\n--- Checking model: {key} -> {model_class.__name__ if model_class else 'Not Found'}")

        if not model_class:
            # print(f"Model class not found for {key}, skipping all rows.")
            valid_indexes = set()
            break

        current_valid_indexes = set()
        records = temp_models.get(key, [])

        for i, record in enumerate(records):
            # print(f"\nRow {i} Record: {record}")
            is_valid = True

            for field, value in record.items():
                try:
                    # Special case for address lookup
                    if key == ('common', 'address') and field == 'address_line_1':
                        original = value
                        value = value.split(',')[0].strip()
                        # print(f"Trying lookup: {model_class.__name__}.{field} = '{value}' (from '{original}')")
                        obj = model_class.objects.get(**{field: value})
                    elif isinstance(value, int):
                        # print(f"Trying lookup: {model_class.__name__}.id = {value}")
                        obj = model_class.objects.get(id=value)
                    elif isinstance(value, str):  # Case-insensitive string lookup
                        # Use `iexact` for exact case-insensitive match, or `icontains` for partial match
                        # print(f"Trying lookup: {model_class.__name__}.{field} = {value.lower()}")
                        obj = model_class.objects.get(**{f"{field}__iexact": value.lower()})
                    else:
                        # print(f"Trying lookup: {model_class.__name__}.{field} = {value}")
                        obj = model_class.objects.get(**{field: value})
                except model_class.DoesNotExist:
                    # print(f"❌ FK error: {model_class.__name__}.{field} = {value} (row {i}) not found.")
                    is_valid = False
                    break

            if is_valid:
                # print(f"✅ Row {i} is valid.")
                current_valid_indexes.add(i)

        valid_indexes &= current_valid_indexes

    # print(f"\n>>> Final valid row indexes: {sorted(valid_indexes)}")

    cleaned_models = {}
    for key, records in temp_models.items():
        cleaned_models[key] = [records[i] for i in sorted(valid_indexes)]

    # print(f"\n>>> Cleaned models result: {cleaned_models}")
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
        removed_new_items = remove_new_items(model_data_map, model_map)
        updated_records = update_record_with_unique_ids(removed_new_items, model_map)
        
        # Get raw data lists
        # Loop through each index
        collected_values = {}

        for (app_label, model_name), records in updated_records.items():
            key = model_name
            
            if model_name == 'wastesource':
                values = [record.get('waste_weight') for record in records if 'waste_weight' in record]
                collected_values[key] = {'waste_weight': values}

            elif model_name == 'wastepickup':
                values = [record.get('pickup_date') for record in records if 'pickup_date' in record]
                collected_values[key] = {'pickup_date': values}

            elif model_name == 'address':
                values = [record.get('address_line_1') for record in records if 'address_line_1' in record]
                collected_values[key] = {'name': values}

            else:
                collected_values[key] = {}
                for field in ['name']:
                    field_values = [record.get(field) for record in records if field in record]
                    if field_values:
                        collected_values[key][field] = field_values

                # values = [record.get('name') for record in records if 'name' in record]
                # collected_values[key] = {'name': values}

        # Extract values
        waste_source_names = collected_values.get('mastersource', {}).get('name', [])
        food_type_names = collected_values.get('commoditymater', {}).get('name', [])
        waste_weights = collected_values.get('wastesource', {}).get('waste_weight', [])
        waste_types = collected_values.get('commoditygroup', {}).get('name', [])
        collector_ids = collected_values.get('collector', {}).get('name', [])
        pickup_dates = collected_values.get('wastepickup', {}).get('pickup_date', [])
        address_names = collected_values.get('address', {}).get('name', [])

        # print(food_type_names,".>>>>>>>>>>>>>>")
        valid_food_types = set(CommodityMater.objects.values_list('name', flat=True))  # Assumes name is unique

        # print(valid_food_types,">>>>>>>>>>")

        # Create WasteSource and WastePickUp objects
        new_data_added = False
        for i in range(len(waste_weights)):
            # Get values for this iteration
            master_source_name = waste_source_names[i] if i < len(waste_source_names) else None
            food_type_name = food_type_names[i] if i < len(food_type_names) else None
            waste_type_name = waste_types[i] if i < len(waste_types) else None
            waste_weight = waste_weights[i]
            pickup_date = pickup_dates[i]
            destination_id = collector_ids[i]
            address_name = address_names[i]
       
        # # Create or get WasteSource
            existing_source = WasteSource.objects.filter(waste_source=master_source_name,
                food_type=food_type_name,
                waste_type=waste_type_name,
                waste_weight=waste_weight).exists()
            if existing_source:
                # return JsonResponse({'message': 'There is No Unique Data'})
                continue

            # print(destination_id,"............")
            waste_source, created = WasteSource.objects.get_or_create(
                waste_source_id=master_source_name,
                food_type_id=food_type_name,
                waste_type_id=waste_type_name,
                waste_weight=waste_weight
            )

        #     # Create or get WastePickUp
            WastePickUp.objects.get_or_create(
                pickup_date=pickup_date,
                waste_source_id=waste_source.id,
                address=address_name,
                image=None,
                destination_id=destination_id
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


def download_temp_getting_names(request):
    cursor = connection.cursor()
    
    # Fetching the parameters safely
    gen_id = request.POST.get('gen_id')
    location_id = request.POST.get('location_id')
    
    # Logging for debugging purposes (you can remove print statements later)
    query = """
        SELECT 
            bd.name,
            ad.address_line_1 || ', ' || ad.address_line_2 || ', ' || ad.city || ', ' || ad.state || ', ' || ad.pin_code AS full_address
        FROM waste_source_group_mastersource AS bd
        JOIN common_address AS ad ON bd.id = ad.id
        WHERE ad.id = %s AND bd.id = %s
    """
    
    try:
        # Execute query safely using parameters
        cursor.execute(query, [location_id, gen_id])  # Passing a list here
        
        columns = [col[0] for col in cursor.description]
        location_list = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
        
        return JsonResponse(location_list, safe=False)
    
    except Exception as e:
        # Handling potential errors
        print(f"Error occurred: {str(e)}")
        return JsonResponse({'error': 'An error occurred while processing the request.'}, status=500)


def download_template(request):
    generator = request.GET.get("generator", "N/A")
    location = request.GET.get("location", "N/A")

    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Template"

    # Define only the needed fields as headers
    headers = [
        "Pickup Date",
        "Generator Name",         # Assuming from WastePickUp or related Collector
        "Address",      # You may need to concatenate address_line_1 and address_line_2
        "Waste Type",   # Custom label for something like WastePickUp.waste_source
        "Food Type",    # Possibly from CommodityMater.name or another related model
        "Total Weight", # This must be derived or pulled from the model accordingly
        "Destination"
    ]


    # Add headers to Excel
    ws.append(headers)

    # Create one blank row with generator & location filled
    row = [""] * len(headers)
    try:
        gen_index = headers.index("Generator Name")
        row[gen_index] = generator
    except ValueError:
        pass

    try:
        loc_index = headers.index("Address")
        row[loc_index] = location
    except ValueError:
        pass

    ws.append(row)

    # Return response
    filename = f"template_{generator}_{location}.xlsx".replace(" ", "_")
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}'
    wb.save(response)
    return response

