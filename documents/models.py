from django.db import models

class DocumentTemplate(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='templates/')

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"