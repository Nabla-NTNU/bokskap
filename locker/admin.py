from django.contrib import admin
from .models import Locker, InactiveLockerReservation


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


class LockerAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'owner')
    list_filter = ('room', HasOwnerListFilter,)
    ordering = ('room', 'locker_number',)
    actions = ('unreserve_locker', 'cut_locker',)
    fields = ('owner', 'owner_name', 'owner_email', 'time_reserved')
    readonly_fields = ('owner_name', 'owner_email')

    def owner_name(self, locker):
        return locker.owner.get_full_name()

    def owner_email(self, locker):
        return locker.owner.email

    def cut_locker(self, request, queryset):
        """Unregister a locker and mark it as cut"""
        for s in queryset.all():
            s.unreserve(lock_cut=True)

    def unreserve_locker(self, request, queryset):
        """Unregister a locker"""
        for s in queryset.all():
            s.unreserve(lock_cut=False)


class InactiveLockerReservationAdmin(admin.ModelAdmin):
    list_display = ('locker', 'owner', 'lock_cut')
    fields = ('locker', 'owner', 'owner_name', 'owner_email',
              'time_reserved', 'time_unreserved', 'lock_cut')
    readonly_fields = ('locker', 'owner_name', 'owner_email')

    def owner_name(self, locker):
        return locker.owner.get_full_name()

    def owner_email(self, locker):
        return locker.owner.email


admin.site.register(Locker, LockerAdmin)
admin.site.register(InactiveLockerReservation, InactiveLockerReservationAdmin)
