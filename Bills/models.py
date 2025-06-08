from django.db import models

class Bill(models.Model):
    slip_no = models.CharField(max_length=20)
    date = models.DateField()
    due_date = models.DateField()
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)

    def __str__(self):
        return f"Slip {self.slip_no} - {self.phone}"

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=50)
    service = models.CharField(max_length=50)
    quantity = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=8, decimal_places=2)
