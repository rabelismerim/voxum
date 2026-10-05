from core.base_internal_user.forms import UserCreationForm
from config.settings import ENABLE_PW
from django.contrib import admin
from django.contrib.auth import login, logout
from django.contrib.auth.admin import UserAdmin
from django.templatetags.static import static
from django.utils.html import format_html
from utils import get_user_model, _

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for managing user groups.

    This class extends the default Django admin GroupAdmin class to provide a customized interface for managing user
    groups.
    It inherits all the functionality of the GroupAdmin class but doesn't add any additional customizations.

    Usage Example:
        @admin.register(Group)
        class CustomGroupAdmin(GroupAdmin):
            pass

    Note:
        This class doesn't introduce any new functionality but allows you to register the Group model in the admin
        interface
        with the default GroupAdmin configuration.
    """
    actions = ['authenticate_user']
    list_display = UserAdmin.list_display + ('is_active',)

    add_form = UserCreationForm
    user_fields = (None, {'fields': ('username',)})

    if ENABLE_PW:
        user_fields = (None, {'fields': ('username', 'password')})
    fieldsets = (
        user_fields,
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'status', 'userpicture', 'user_img')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'login_date', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'login_date'),
        }),
    )
    list_filter = ('is_staff', 'is_active', 'groups')

    list_display = (
        'show_image', 'id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'created_at', 'updated_at', 'login_date', 'is_active')
    readonly_fields = ('show_image', 'created_at', 'updated_at')

    def show_image(self, obj):
        image_url = obj.get_img_url() or static('src/vue/dist/icon-app.svg')
        return format_html('<img src="{}" width="25" height="25" />', image_url)

    show_image.allow_tags = True
    show_image.short_description = _('Image')

    def authenticate_user(self, request, queryset):
        query_count = queryset.count()

        if query_count > 1:
            raise ValueError('Logar apenas um unico usuário')

        user = queryset.first()
        logout(request)
        login(request, user)