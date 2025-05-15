from django.views import View
from django.http import JsonResponse
import json
from django.contrib.auth import get_user_model
from apps.users.services.mfa_service import MFAService

User = get_user_model()

class AjaxLoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            # Check if user exists
            user = User.objects.filter(email=email).first()
            if not user:
                return JsonResponse({'success': False, 'message': 'Invalid email or password'}, status=400)

            # Check if user is active
            if not user.is_active:
                return JsonResponse({'success': False, 'message': 'Account is inactive. Please activate your email.'}, status=400)

            # Check credentials
            if not user.check_password(password):
                return JsonResponse({'success': False, 'message': 'Invalid email or password'}, status=400)

            # ✅ Do NOT login yet → generate OTP and return session token
            session_token = MFAService.generate_otp(user)
            request.session['mfa_user_id'] = user.id

            return JsonResponse({
                'success': True,
                'mfa': True,
                'redirect_url': '/auth/verify-otp/',
                'session_token': str(session_token)
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
