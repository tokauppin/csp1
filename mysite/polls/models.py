
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class Poll(models.Model):
    question = models.CharField(max_length=255, blank=False, null=False)
    option_one = models.CharField(max_length=50)
    option_two = models.CharField(max_length=50)
    option_three = models.CharField(max_length=50)

    option_one_votes = models.IntegerField(default=0)
    option_two_votes = models.IntegerField(default=0)
    option_three_votes = models.IntegerField(default=0)
    user_has_voted = models.BooleanField(default=False)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.question