from django.contrib import admin
from django.utils.html import format_html
from .models import Lay, DepositAddress, DepositRotation, WithdrawRequest

@admin.register(Lay)
class LayAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "total_odds", "stake_amount", "win_payout",
        "loss_payout", "status", "created_at", "image_tag"
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "file_name")
    readonly_fields = ("id", "created_at", "image_tag", "file")

    def image_tag(self, obj):
        if obj.file:
            return format_html('<img src="{}" width="100" style="object-fit:contain;" />', obj.file.url)
        return "-"
    image_tag.short_description = "Preview"

@admin.register(DepositAddress)
class DepositAddressAdmin(admin.ModelAdmin):
    list_display = ("index", "address")
    ordering = ("index",)
    search_fields = ("address",)

@admin.register(DepositRotation)
class DepositRotationAdmin(admin.ModelAdmin):
    list_display = ("current_index", "last_updated")
    readonly_fields = ("last_updated",)

@admin.register(WithdrawRequest)
class WithdrawRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "address", "created_at")
    search_fields = ("user__email", "address")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)