from django.db import models

# Create your models here.

class PowerPointPresentation(models.Model):
    text = models.TextField()
    file = models.FileField(upload_to='presentations/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Presentation created at {self.created_at}"

class PresentationData(models.Model):
    title = models.CharField(max_length=255, default="title")
    json_data = models.JSONField()
    # presentation = models.ForeignKey(PowerPointPresentation, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
