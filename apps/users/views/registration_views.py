import json
from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth import get_user_model
from apps.users.services.registration_service import RegistrationService

User = get_user_model()

class RegisterUserView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            name = data.get("name", "").strip()
            email = data.get("email", "").strip()
            phone = data.get("phone", "").strip()

            # Backend validations
            if not name or not email or not phone:
                return JsonResponse({"success": False, "message": "All fields are required."})

            if not phone.isdigit() or len(phone) != 10:
                return JsonResponse({"success": False, "message": "Phone must be 10 digits."})

            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({"success": False, "message": "Invalid email format."})
            
            # 4. Duplicate checks
            if User.objects.filter(email=email).exists():
                return JsonResponse({"success": False, "message": "Email is already registered."})

            if User.objects.filter(phone=phone).exists():
                return JsonResponse({"success": False, "message": "Phone number is already in use."})


            success, message = RegistrationService.register_user(name, email, phone, request)
            if success:
                return JsonResponse({ "success": True })
            return JsonResponse({ "success": False, "message": message })
        except Exception as e:
            return JsonResponse({ "success": False, "message": str(e) })

