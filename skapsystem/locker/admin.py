from django.contrib import admin
from locker.models import Locker

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

admin.site.register(Locker, LockerAdmin)
