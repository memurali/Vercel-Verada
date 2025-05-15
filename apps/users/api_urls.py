from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from apps.users.views.auth_views import (
    register_view, 
    login_view, 
    otp_verify_view,
    logout_view
)
from apps.users.views.ajax_views import AjaxLoginView
from apps.users.views.usermanagement_views import dashboard_usermanagement_view
from apps.users.views.add_user_views import ajax_create_user, user_form_view
from apps.users.views.user_role_views import role_form_view, assign_role_ajax
from apps.users.views.user_role_manage_views import user_roles_dashboard, update_user_role_ajax
from apps.users.views.role_permission_views import permission_form_view, assign_permissions_ajax, get_role_permissions
from apps.users.views.edit_user_handler_views import edit_user_view, update_user_ajax

from apps.users.views.account_activation import ActivateAccountView
from apps.users.views.registration_views import RegisterUserView
from apps.users.views.change_password_views import ChangePasswordTokenView

from apps.users.views.otp_views import OtpVerifyView 

from apps.users.views.profile_views import profile_edit_view, submit_profile_data, company_profile_dashboard

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path("logout/", logout_view, name="logout"),
    path('login/verify/', otp_verify_view, name='otp_verify'),
    path("api/auth/ajax-login/", AjaxLoginView.as_view(), name="ajax_login"),

    #USER MANAGEEMT
    path("dashboard/usermanagement/", dashboard_usermanagement_view, name="dashboard_usermanagement"),
    path("user/add/form/", user_form_view, name="user_add_form"),
    path("ajax-create/", ajax_create_user, name="ajax_create_user"),
    path("roles/form/", role_form_view, name="role_form"),
    path("roles/assign/", assign_role_ajax, name="assign_role"),
    path("user-roles/", user_roles_dashboard, name="dashboard_userroles"),
    path("update-role/", update_user_role_ajax, name="update_user_role"),
    path("permissions/form/", permission_form_view, name="permission_form"),
    path("permissions/assign/", assign_permissions_ajax, name="assign_permissions"),
    path("user/edit/<int:user_id>/", edit_user_view, name="edit_user"),
    path("user/update/", update_user_ajax, name="update_user"),
    # urls.py
    path('get-role-permissions/', get_role_permissions, name='get_role_permissions'),


    #REGITRATION HANDLING
    path("api/auth/ajax-register/", RegisterUserView.as_view(), name="ajax_register"),
    path("activate/<str:token>/", ActivateAccountView.as_view(), name="activate_account"),
    path("change-password/", ChangePasswordTokenView.as_view(), name="change_password_token"),

    path("auth/verify-otp/", OtpVerifyView.as_view(), name="verify_otp"),

    #PROFILE
    path('profile/dashboard/', company_profile_dashboard, name='company_profile_dashboard'),
    path('profile/edit/<int:user_id>/', profile_edit_view, name='profile_edit_form'),
    path('profile/add/', profile_edit_view, name='profile_add_form'),
    path("profile/submit/", submit_profile_data, name="submit_profile_data"),
]
