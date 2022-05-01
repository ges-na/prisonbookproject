from django.db import models
from django.contrib.auth.models import User


class Person(models.Model):
    inmate_number = models.CharField(max_length=50)
    last_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_sent = models.DateField(null=True, blank=True)
    package_count = models.PositiveSmallIntegerField(default=0)
    # I think this is pulled from FK to Letters
    pending_letter = models.DateField(null=True, blank=True)
    eligibility = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by=models.ForeignKey(User, null=True, related_name='person_modified_by_user', on_delete=models.SET_NULL)
    created_by=models.ForeignKey(User, null=True, related_name='person_created_by_user', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('-pending_letter',)
        verbose_name_plural = "people"

    def __str__(self):
        return self.last_name

    @property
    def current_prison(self):
        if person_prison := self.prisons.filter(current=True).first():
            return person_prison.prison.name


class Prison(models.Model):
    name = models.CharField(max_length=200)
    prison_type = models.CharField(max_length=50)
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=200)
    # WHAT IS GREE
    # Probably omit restrictions ultimately
    restrictions = models.CharField(max_length=200, null=True)
    notes = models.CharField(max_length=200, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by=models.ForeignKey(User, null=True, related_name='prison_modified_by_user', on_delete=models.SET_NULL)
    created_by=models.ForeignKey(User, null=True, related_name='prison_created_by_user', on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Letter(models.Model):
    date_received = models.DateField(null=True, blank=True)
    date_processed = models.DateField(null=True, blank=True)
    workflow_stage = models.CharField(max_length=200)
    notes = models.CharField(max_length=200, null=True)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by=models.ForeignKey(User, null=True, related_name='letter_modified_by_user', on_delete=models.SET_NULL)
    created_by=models.ForeignKey(User, null=True, related_name='letter_created_by_user', on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.person.last_name} - {self.date_received}"


class PersonPrison(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='prisons')
    prison = models.ForeignKey('Prison', on_delete=models.CASCADE, related_name='people')
    current = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by=models.ForeignKey(User, null=True, related_name='personprison_modified_by_user', on_delete=models.SET_NULL)
    created_by=models.ForeignKey(User, null=True, related_name='personprison_created_by_user', on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.prison.name} - {self.person.last_name}"
