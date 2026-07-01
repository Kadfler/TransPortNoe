from django.contrib import admin
from .models import DocumentTemplate


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    # Отображение колонок в таблице
    list_display = ('id', 'name', 'description')
    # Клик по имени открывает редактирование
    list_display_links = ('id', 'name')
    # Поиск по названию
    search_fields = ('name',)

    # Меняем заголовки колонок, если они не заданы в модели
    DocumentTemplate._meta.get_field('name').verbose_name = 'Название шаблона'
    DocumentTemplate._meta.get_field('description').verbose_name = 'Описание'
    DocumentTemplate._meta.get_field('file').verbose_name = 'Файл шаблона'