from django.contrib import admin, messages
from django.contrib.auth.models import User
from .models import Locker, Ownership, RegistrationRequest, LockerReservedException


class HasOwnerListFilter(admin.SimpleListFilter):
    title = 'status'
    parameter_name = 'hasowner'

    def lookups(self, request, model_admin):
        return (
            ('busy', 'Opptatte skap'),
            ('empty', 'Tomme skap'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'busy':
            return queryset.filter(user__isnull=False)
        if self.value() == 'empty':
            return queryset.filter(user__isnull=True)

        
class IsUnregistered(admin.SimpleListFilter):
    title = 'status'
    parameter_name = 'isunregistered'

    def lookups(self, request, model_admin):
        return (
            ('inactive', 'Ikke-aktiv'),
            ('active', 'Aktiv'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'inactive':
            return queryset.filter(time_unreserved__isnull=False)
        if self.value() == 'active':
            return queryset.filter(time_unreserved__isnull=True)
    


@admin.register(Locker)
class LockerAdmin(admin.ModelAdmin):
    list_display = ('locker_number', 'room')
    ordering = ('room', 'locker_number',)
    actions = ('unreserve_locker', 'cut_locker',)
    fields = ('locker_number', 'room')
    readonly_fields = ('locker_number', 'room')

@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ("user", "locker", "time_unreserved", 'is_reserved')
    list_filter = (IsUnregistered,)
    fields = ("user", "locker", "time_reserved", "time_unreserved")
    search_fields = ("^locker__room", "^locker__locker_number", "^user__username")
    readonly_fields = ("user", "locker", "time_reserved", "time_unreserved")
    actions = ('unreserve',)

    def is_reserved(self, ownership):
        return bool(ownership.time_unreserved is None)
    is_reserved.boolean = True
    is_reserved.short_description = "Aktivt"
    
    def unreserve(self, request, queryset):
        for s in queryset.all():
            s.unregister()
    
@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    actions = ("confirm",)
    list_display = ("username", "locker", "creation_time", "confirmation_time")
    list_filter = ('locker__room',)
    search_fields = ('locker__room', '^locker__locker_number', '^username')

    def confirm(self, request, queryset):
        for reg_request in queryset:
            try:
                reg_request.confirm()
            except LockerReservedException as e: # Locker allready has an active ownership.
                messages.error(request, str(e))
            else:
                self.message_user(request, f"{reg_request.locker} confirmed.")
