from django.db import models

class slip(models.Model):
    slip_no = models.IntegerField()
    date = models.DateField()
    due_date = models.DateField()
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    amount = models.IntegerField()

    def __str__(self):
        return f"Slip {self.slip_no} - {self.phone}"

class items(models.Model):
    slip = models.ForeignKey(slip, related_name='items', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=50)
    service = models.CharField(max_length=50)
    quantity = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=8, decimal_places=2)
