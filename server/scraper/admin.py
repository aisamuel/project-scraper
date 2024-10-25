from django.contrib import admin

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "birthday"]
    list_display_links = ["first_name", "last_name"]
