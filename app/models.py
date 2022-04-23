from django.db import models


class Inmate(models.Model):
    inmate_number = models.CharField(max_length=50)
    last_name = models.CharField(max_length=200)
    last_sent = models.DateField(null=True, blank=True)
    package_count = models.PositiveSmallIntegerField(default=0)
    pending_letter = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ('-pending_letter',)

    def __str__(self):
        return self.last_name

    @property
    def current_prison(self):
        if inmate_prison := self.prisons.filter(current=True).first():
            return inmate_prison.prison.name


class Prison(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class InmatePrison(models.Model):
    inmate = models.ForeignKey('Inmate', on_delete=models.CASCADE, related_name='prisons')
    prison = models.ForeignKey('Prison', on_delete=models.CASCADE, related_name='inmates')
    current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.prison.name} - {self.inmate.last_name}"
