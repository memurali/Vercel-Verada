# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from apps.users.models import Client, User

from django.http import JsonResponse
from django.views.decorators.http import require_POST


@login_required(login_url='login')
def company_profile_dashboard(request):
    users_with_profile = User.objects.select_related('client').exclude(is_staff=True, is_superuser=True)
    return render(request, 'profile/profile.html', {
        'users': users_with_profile
    })


@login_required(login_url='login')
def profile_edit_view(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, pk=user_id)
        client = user.client or Client()
    else:
        user = request.user
        client = user.client or Client()

    return render(request, 'profile/profile_change.html', {
        'user_obj': user,
        'client': client,
    })

@require_POST
@login_required
def submit_profile_data(request):
    try:
        user_id = request.POST.get("user_id")

        if user_id:
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({"success": False, "message": "User not found."}, status=404)
        else:
            target_user = request.user

        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()

        # 4. Duplicate checks
        if User.objects.filter(email=email).exclude(id=target_user.id).exists():
            return JsonResponse({"success": False, "message": "Email is already registered."})

        if User.objects.filter(phone=phone).exclude(id=target_user.id).exists():
            return JsonResponse({"success": False, "message": "Phone number is already in use."})

        # --- Update User Info ---
        target_user.first_name = request.POST.get("first_name", "").strip()
        target_user.last_name = request.POST.get("last_name", "").strip()
        target_user.company_name = request.POST.get("company_name", "").strip()
        target_user.email = email
        target_user.phone = phone
        target_user.save()

        # --- Update or Create Client ---
        if not target_user.client:
            client = Client()  # Create a new client
            target_user.client = client  # Assign it first
        else:
            client = target_user.client

        client.company_name = request.POST.get("company_name", "").strip()
        client.company_address = request.POST.get("company_address", "").strip()
        client.company_email = email
        client.company_phone = phone

        logo = request.FILES.get("company_logo")
        if logo:
            client.company_logo = logo

        client.save()
        target_user.save()

        return JsonResponse({"success": True, "message": "Profile updated successfully."})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

