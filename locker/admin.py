"""
Admin interface for locker app
"""
from django.contrib import admin, messages
from .models import Locker, Ownership, RegistrationRequest, LockerReservedException


class IsUnregistered(admin.SimpleListFilter):
    """
    Filters lockers by whether lockers are registered
    """
    title = 'status'
    parameter_name = 'isunregistered'

    def lookups(self, request, model_admin):
        return (
            ('inactive', 'Ikke-aktiv'),
            ('active', 'Aktiv'),
        )

    def queryset(self, request, queryset):
        if self.value():
            is_active = self.value() == 'active'
            return queryset.filter(time_unreserved__isnull=is_active)
        return None


@admin.register(Locker)
class LockerAdmin(admin.ModelAdmin):
    """Admin interface for Locker mode"""
    list_display = ('locker_number', 'room')
    ordering = ('room', 'locker_number',)
    actions = ('unreserve_locker', 'cut_locker',)
    fields = ('locker_number', 'room')
    readonly_fields = ('locker_number', 'room')


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    """Admin interface for Ownership model"""
    list_display = ("user", "locker", "time_unreserved", 'is_active')
    list_filter = (IsUnregistered,)
    fields = ("user", "locker", "time_reserved", "time_unreserved")
    search_fields = ("^locker__room", "^locker__locker_number", "^user__username")
    readonly_fields = ("user", "locker", "time_reserved", "time_unreserved")
    actions = ('unreserve',)

    def is_active(self, ownership):
        """Return whether ownership is active"""
        return ownership.is_active()
    is_active.boolean = True
    is_active.short_description = "Aktivt"

    def unreserve(self, request, queryset):
        """Make all selected ownerships inactive"""
        for owenership in queryset.all():
            owenership.unregister()


@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    """Admin interface for reqistration requests"""
    actions = ("confirm",)
    list_display = ("username", "locker", "creation_time", "confirmation_time")
    list_filter = ('locker__room',)
    search_fields = ('locker__room', '^locker__locker_number', '^username')

    def confirm(self, request, queryset):
        """Confirm selected registration requests"""
        for reg_request in queryset:
            try:
                reg_request.confirm()
            except LockerReservedException as ex: # Locker already has an active ownership.
                messages.error(request, str(ex))
            else:
                self.message_user(request, f"{reg_request.locker} confirmed.")
