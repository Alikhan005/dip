from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        TEACHER = "teacher", "Преподаватель"
        PROGRAM_LEADER = "program_leader", "Руководитель программы"
        DEAN = "dean", "Декан"
        UMU = "umu", "УМУ"
        ADMIN = "admin", "Админ"

    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.TEACHER,
    )

    faculty = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)

    @property
    def is_teacher_like(self) -> bool:
        return self.role in {self.Role.TEACHER, self.Role.DEAN}

    @property
    def can_edit_content(self) -> bool:
        return self.role in {self.Role.TEACHER, self.Role.DEAN, self.Role.ADMIN}

    @property
    def can_view_courses(self) -> bool:
        return self.role in {self.Role.TEACHER, self.Role.DEAN, self.Role.ADMIN}

    @property
    def can_view_shared_courses(self) -> bool:
        return self.role in {
            self.Role.TEACHER,
            self.Role.PROGRAM_LEADER,
            self.Role.DEAN,
            self.Role.ADMIN,
        }

    def __str__(self):
        return self.get_full_name() or self.username
