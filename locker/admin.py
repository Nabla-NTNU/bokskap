from django.contrib import admin
from .models import Locker, Ownership, RegistrationRequest


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
            return queryset.filter(owner__isnull=False)
        if self.value() == 'empty':
            return queryset.filter(owner__isnull=True)

class IsUnregistered(admin.SimpleListFilter):
    title = 'status'
    parameter_name = 'isunregistered'

    def lookups(self, request, model_admin):
        return (
            ('unregistered', 'Avregistrerte'),
            ('registered', 'Registrerte'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'unregistered':
            return queryset.filter(time_unreserved__isnull=False)
        if self.value() == 'registered':
            return queryset.filter(time_unreserved__isnull=True)
    


@admin.register(Locker)
class LockerAdmin(admin.ModelAdmin):
    list_display = ('locker_number', 'room')
    ordering = ('room', 'locker_number',)
    actions = ('unreserve_locker', 'cut_locker',)
    fields = ('locker_number', 'room')
    readonly_fields = ('locker_number', 'room')

    def owner_name(self, locker):
        return locker.owner.get_full_name()

    def owner_email(self, locker):
        return locker.owner.email

    def cut_locker(self, request, queryset):
        """Unregister a locker and mark it as cut"""
        for s in queryset.all():
            s.unregister(lock_cut=True)

    def unreserve_locker(self, request, queryset):
        """Unregister a locker"""
        for s in queryset.all():
            s.unregister(lock_cut=False)

@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ("owner", "locker", "time_unreserved", 'is_unreserved')
    list_filter = (IsUnregistered,)
    fields = ("owner", "locker", "time_reserved", "time_unreserved", "lock_cut")
    readonly_fields = ("owner", "locker", "time_reserved", "time_unreserved")
    actions = ('unreserve',)

    def is_unreserved(self, Ownership):
        return bool(Ownership.time_unreserved is not None)
    
    def unreserve(self, request, queryset):
        for s in queryset.all():
            s.unregister(lock_cut=False)
    
@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    actions = ("confirm",)
    list_display = ("username", "locker", "creation_time", "confirmation_time")
    list_filter = ('locker__room',)
    search_fields = ('locker__room', '^locker__locker_number', '^username')

    def confirm(self, request, queryset):
        for reg_request in queryset:
            reg_request.confirm()
