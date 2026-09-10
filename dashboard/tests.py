from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from courses.models import Course
from payments.models import PlanType, UserCourseAccess
from dashboard.models import StudentComment

User = get_user_model()


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff_dashboard',
            password='StaffPass123!',
            is_staff=True,
        )
        self.student_old = User.objects.create_user(
            username='555111001',
            phone_number='555111001',
            password='Pass123!',
            student_name='Old Student',
            parent_name='Parent A',
            grade='VI',
            book_author='Author',
        )
        self.student_new = User.objects.create_user(
            username='555111002',
            phone_number='555111002',
            password='Pass123!',
            student_name='New Student',
            parent_name='Parent B',
            grade='VII',
            book_author='Author',
        )
        self.course = Course.objects.create(
            title='VI კლასის მათემატიკა',
            grade='VI',
            short_description='Short',
            long_description='Long',
            instructor_name='Teacher',
            duration='10h',
            lessons_count=5,
            video_url='https://youtube.com/embed/test',
            price=Decimal('50.00'),
        )

    def test_non_staff_cannot_access_dashboard(self):
        self.client.force_login(self.student_old)
        res = self.client.get(reverse('dashboard:students'))
        self.assertEqual(res.status_code, 302)
        self.assertIn('/accounts/login', res.url)

    def test_staff_sees_paginated_students_ordered_by_latest_enrollment(self):
        UserCourseAccess.objects.create(
            user=self.student_old,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            is_active=True,
            auto_renew=False,
            starts_at=timezone.now() - timedelta(days=5),
            expires_at=timezone.now() + timedelta(days=25),
        )
        UserCourseAccess.objects.create(
            user=self.student_new,
            course=self.course,
            plan_type=PlanType.YEARLY,
            is_active=True,
            auto_renew=False,
            starts_at=timezone.now() - timedelta(days=1),
            expires_at=timezone.now() + timedelta(days=364),
        )
        self.client.force_login(self.staff)
        res = self.client.get(reverse('dashboard:students'))
        self.assertEqual(res.status_code, 200)
        students = list(res.context['students'])
        self.assertEqual(students[0].pk, self.student_new.pk)
        self.assertEqual(students[1].pk, self.student_old.pk)
        self.assertContains(res, 'New Student')
        self.assertContains(res, 'Old Student')

    def test_staff_can_grant_course_access_without_payment(self):
        self.client.force_login(self.staff)
        res = self.client.post(
            reverse('dashboard:grant_access', kwargs={'user_id': self.student_old.pk}),
            data={'course': self.course.pk, 'plan_type': PlanType.YEARLY},
        )
        self.assertEqual(res.status_code, 302)
        access = UserCourseAccess.objects.get(user=self.student_old, course=self.course)
        self.assertTrue(access.is_valid_now())
        self.assertFalse(access.auto_renew)
        self.assertIsNone(access.last_order_id)

    def test_pagination_limits_to_twenty_students(self):
        for i in range(25):
            User.objects.create_user(
                username=f'555200{i:03d}',
                phone_number=f'555200{i:03d}',
                password='Pass123!',
                student_name=f'Student {i}',
                parent_name='Parent',
                grade='VI',
                book_author='Author',
            )
        self.client.force_login(self.staff)
        res = self.client.get(reverse('dashboard:students'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['students']), 20)
        self.assertEqual(res.context['page_obj'].paginator.num_pages, 2)

    def test_filter_enrolled_students_only(self):
        UserCourseAccess.objects.create(
            user=self.student_old,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            is_active=True,
            auto_renew=False,
            starts_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
        )
        self.client.force_login(self.staff)
        res = self.client.get(reverse('dashboard:students'), {'status': 'enrolled'})
        self.assertEqual(res.status_code, 200)
        students = list(res.context['students'])
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].pk, self.student_old.pk)

    def test_filter_not_enrolled_students_only(self):
        UserCourseAccess.objects.create(
            user=self.student_old,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            is_active=True,
            auto_renew=False,
            starts_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
        )
        self.client.force_login(self.staff)
        res = self.client.get(reverse('dashboard:students'), {'status': 'not_enrolled'})
        self.assertEqual(res.status_code, 200)
        students = list(res.context['students'])
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].pk, self.student_new.pk)

    def test_filter_by_course(self):
        course_b = Course.objects.create(
            title='VII კლასის მათემატიკა',
            grade='VII',
            short_description='Short',
            long_description='Long',
            instructor_name='Teacher',
            duration='10h',
            lessons_count=5,
            video_url='https://youtube.com/embed/test',
            price=Decimal('50.00'),
        )
        UserCourseAccess.objects.create(
            user=self.student_old,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            is_active=True,
            auto_renew=False,
            starts_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
        )
        UserCourseAccess.objects.create(
            user=self.student_new,
            course=course_b,
            plan_type=PlanType.MONTHLY,
            is_active=True,
            auto_renew=False,
            starts_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
        )
        self.client.force_login(self.staff)
        res = self.client.get(reverse('dashboard:students'), {'course': self.course.pk})
        self.assertEqual(res.status_code, 200)
        students = list(res.context['students'])
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].pk, self.student_old.pk)

    def test_filter_by_course_combined_with_enrollment(self):
        UserCourseAccess.objects.create(
            user=self.student_old,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            is_active=True,
            auto_renew=False,
            starts_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
        )
        self.client.force_login(self.staff)
        res = self.client.get(
            reverse('dashboard:students'),
            {'status': 'enrolled', 'course': self.course.pk},
        )
        self.assertEqual(res.status_code, 200)
        students = list(res.context['students'])
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].pk, self.student_old.pk)

    def test_search_by_student_name(self):
        self.client.force_login(self.staff)
        res = self.client.get(
            reverse('dashboard:students'),
            {'search_field': 'student_name', 'search_q': 'New'},
        )
        self.assertEqual(res.status_code, 200)
        students = list(res.context['students'])
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].pk, self.student_new.pk)

    def test_search_by_parent_name(self):
        self.client.force_login(self.staff)
        res = self.client.get(
            reverse('dashboard:students'),
            {'search_field': 'parent_name', 'search_q': 'Parent A'},
        )
        self.assertEqual(res.status_code, 200)
        students = list(res.context['students'])
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].pk, self.student_old.pk)

    def test_search_by_phone(self):
        self.client.force_login(self.staff)
        res = self.client.get(
            reverse('dashboard:students'),
            {'search_field': 'phone', 'search_q': '555111002'},
        )
        self.assertEqual(res.status_code, 200)
        students = list(res.context['students'])
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].pk, self.student_new.pk)

    def test_search_ignored_without_field(self):
        self.client.force_login(self.staff)
        res = self.client.get(reverse('dashboard:students'), {'search_q': 'New'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['students']), 2)

    def test_search_ignores_enrollment_filter(self):
        UserCourseAccess.objects.create(
            user=self.student_old,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            is_active=True,
            auto_renew=False,
            starts_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
        )
        self.client.force_login(self.staff)
        res = self.client.get(
            reverse('dashboard:students'),
            {
                'status': 'not_enrolled',
                'search_field': 'student_name',
                'search_q': 'Old',
            },
        )
        self.assertEqual(res.status_code, 200)
        students = list(res.context['students'])
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].pk, self.student_old.pk)

    def test_search_ignores_course_filter(self):
        course_b = Course.objects.create(
            title='VII კლასის მათემატიკა',
            grade='VII',
            short_description='Short',
            long_description='Long',
            instructor_name='Teacher',
            duration='10h',
            lessons_count=5,
            video_url='https://youtube.com/embed/test',
            price=Decimal('50.00'),
        )
        UserCourseAccess.objects.create(
            user=self.student_old,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            is_active=True,
            auto_renew=False,
            starts_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
        )
        self.client.force_login(self.staff)
        res = self.client.get(
            reverse('dashboard:students'),
            {
                'course': course_b.pk,
                'search_field': 'student_name',
                'search_q': 'Old',
            },
        )
        self.assertEqual(res.status_code, 200)
        students = list(res.context['students'])
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].pk, self.student_old.pk)

    def test_grant_redirect_preserves_search(self):
        self.client.force_login(self.staff)
        res = self.client.post(
            reverse('dashboard:grant_access', kwargs={'user_id': self.student_old.pk}),
            data={
                'course': self.course.pk,
                'plan_type': PlanType.YEARLY,
                'list_search_field': 'student_name',
                'list_search_q': 'Old',
            },
        )
        self.assertEqual(res.status_code, 302)
        self.assertIn('search_field=student_name', res.url)
        self.assertIn('search_q=Old', res.url)

    def test_staff_can_add_and_see_student_comment(self):
        self.client.force_login(self.staff)
        res = self.client.post(
            reverse('dashboard:add_comment', kwargs={'user_id': self.student_old.pk}),
            data={'text': 'Needs follow-up call'},
        )
        self.assertEqual(res.status_code, 302)
        self.assertTrue(
            StudentComment.objects.filter(
                student=self.student_old,
                text='Needs follow-up call',
            ).exists()
        )
        list_res = self.client.get(reverse('dashboard:students'))
        self.assertContains(list_res, 'Needs follow-up call')
        self.assertContains(list_res, 'comment-bell__count')

    def test_staff_can_delete_student_comment(self):
        comment = StudentComment.objects.create(
            student=self.student_old,
            author=self.staff,
            text='Remove me',
        )
        self.client.force_login(self.staff)
        res = self.client.post(
            reverse(
                'dashboard:delete_comment',
                kwargs={'user_id': self.student_old.pk, 'comment_id': comment.pk},
            )
        )
        self.assertEqual(res.status_code, 302)
        self.assertFalse(StudentComment.objects.filter(pk=comment.pk).exists())

    def test_empty_comment_is_rejected(self):
        self.client.force_login(self.staff)
        res = self.client.post(
            reverse('dashboard:add_comment', kwargs={'user_id': self.student_old.pk}),
            data={'text': '   '},
        )
        self.assertEqual(res.status_code, 302)
        self.assertEqual(StudentComment.objects.count(), 0)

    def test_cannot_delete_comment_for_wrong_student(self):
        comment = StudentComment.objects.create(
            student=self.student_old,
            author=self.staff,
            text='Keep me',
        )
        self.client.force_login(self.staff)
        res = self.client.post(
            reverse(
                'dashboard:delete_comment',
                kwargs={'user_id': self.student_new.pk, 'comment_id': comment.pk},
            )
        )
        self.assertEqual(res.status_code, 404)
        self.assertTrue(StudentComment.objects.filter(pk=comment.pk).exists())

    def test_non_staff_cannot_add_comment(self):
        self.client.force_login(self.student_old)
        res = self.client.post(
            reverse('dashboard:add_comment', kwargs={'user_id': self.student_old.pk}),
            data={'text': 'Should not work'},
        )
        self.assertEqual(res.status_code, 302)
        self.assertIn('/accounts/login', res.url)
        self.assertEqual(StudentComment.objects.count(), 0)
