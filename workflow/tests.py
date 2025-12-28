from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from catalog.models import Course
from syllabi.models import Syllabus
from workflow.models import SyllabusStatusLog
from workflow.services import change_status

User = get_user_model()


class WorkflowRoleTests(TestCase):
    def _create_user(self, username: str, role: str) -> User:
        return User.objects.create_user(username=username, password="pass1234", role=role)

    def _create_course(self, owner: User, code: str = "CS101") -> Course:
        return Course.objects.create(
            owner=owner,
            code=code,
            available_languages="ru",
        )

    def test_umu_can_approve_submitted_umu(self):
        teacher = self._create_user("teacher_user", "teacher")
        umu = self._create_user("umu_user", "umu")
        course = self._create_course(teacher)
        syllabus = Syllabus.objects.create(
            course=course,
            creator=teacher,
            semester="Fall 2025",
            academic_year="2025-2026",
            status=Syllabus.Status.SUBMITTED_UMU,
        )

        change_status(umu, syllabus, Syllabus.Status.APPROVED_UMU, "ok")

        syllabus.refresh_from_db()
        self.assertEqual(syllabus.status, Syllabus.Status.APPROVED_UMU)
        self.assertTrue(
            SyllabusStatusLog.objects.filter(
                syllabus=syllabus,
                to_status=Syllabus.Status.APPROVED_UMU,
                changed_by=umu,
            ).exists()
        )

    def test_umu_cannot_approve_own_syllabus(self):
        umu = self._create_user("umu_author", "umu")
        course = self._create_course(umu)
        syllabus = Syllabus.objects.create(
            course=course,
            creator=umu,
            semester="Fall 2025",
            academic_year="2025-2026",
            status=Syllabus.Status.SUBMITTED_UMU,
        )

        with self.assertRaises(PermissionDenied):
            change_status(umu, syllabus, Syllabus.Status.APPROVED_UMU, "ok")

        syllabus.refresh_from_db()
        self.assertEqual(syllabus.status, Syllabus.Status.SUBMITTED_UMU)

    def test_dean_cannot_approve_own_syllabus(self):
        dean = self._create_user("dean_author", "dean")
        course = self._create_course(dean, code="CS202")
        syllabus = Syllabus.objects.create(
            course=course,
            creator=dean,
            semester="Fall 2025",
            academic_year="2025-2026",
            status=Syllabus.Status.SUBMITTED_DEAN,
        )

        with self.assertRaises(PermissionDenied):
            change_status(dean, syllabus, Syllabus.Status.APPROVED_DEAN, "ok")

        syllabus.refresh_from_db()
        self.assertEqual(syllabus.status, Syllabus.Status.SUBMITTED_DEAN)

    def test_wrong_status_rejected(self):
        teacher = self._create_user("teacher_author", "teacher")
        dean = self._create_user("dean_user", "dean")
        course = self._create_course(teacher, code="CS303")
        syllabus = Syllabus.objects.create(
            course=course,
            creator=teacher,
            semester="Fall 2025",
            academic_year="2025-2026",
            status=Syllabus.Status.DRAFT,
        )

        with self.assertRaises(PermissionDenied):
            change_status(dean, syllabus, Syllabus.Status.APPROVED_DEAN, "ok")

        syllabus.refresh_from_db()
        self.assertEqual(syllabus.status, Syllabus.Status.DRAFT)
