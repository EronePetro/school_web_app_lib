from django.db import models
from django.utils import timezone
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Categories"


class Row(models.Model):
    shelve = models.CharField(max_length=20, help_text="Eg. 1, 2, 3 etc")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return "shelf label: %s of %s" %(self.shelve, self.category.category_name)
    


class Column(models.Model):
    column_name = models.CharField(max_length=50, help_text="Eg. A")
    row = models.ForeignKey(Row, on_delete=models.CASCADE)

    def __str__(self):
        return "Column %s of %s" %(self.column_name, self.row.shelve)


class Book(models.Model):
    book_serial_no = models.CharField(max_length=20, unique=True)
    book_name = models.CharField(max_length=100)
    column = models.ForeignKey(Column, on_delete=models.CASCADE)

    def __str__(self):
        return self.book_serial_no


class FormStreamYear(models.Model):
    form_label = models.PositiveSmallIntegerField(help_text="Eg. 1, 2, 3 and 4")
    stream = models.CharField(max_length=20, help_text="Eg. White, Green, Blue etc.")
    year = models.PositiveSmallIntegerField(help_text="Eg. 2020, 2022 and 2024")
    teacher = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return "Form %d %s, %d - %s" %(self.form_label, self.stream, self.year, self.teacher.full_name)

    class Meta:
        verbose_name_plural = "Streams"
        ordering = ['form_label']


class Student(models.Model):
    student_admission_no = models.CharField(max_length=50, unique=True)
    student_name = models.CharField(max_length=100)
    form_stream_year = models.ForeignKey(FormStreamYear, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" %(self.student_name, self.student_admission_no)


class Staff(models.Model):
    staff_member_name = models.CharField(max_length=100)
    staff_member_no = models.CharField(max_length=50, unique=True)
    contact = PhoneNumberField()

    def __str__(self):
        return "{0} - {1} - {2}".format(self.staff_member_name, self.staff_member_no, self.contact)

    class Meta:
        verbose_name_plural = "Staff members"


class Borrowed(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    date_borrowed = models.DateTimeField(default=timezone.now)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, blank=True, null=True)
    librarian = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.book.book_serial_no


    class Meta:
        verbose_name_plural = "Borrowed books"


class Counter(models.Model):
    counts = models.PositiveSmallIntegerField()
    week_num = models.PositiveSmallIntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{0} counts on {1}".format(self.counts, self.date)


class School(models.Model):
    school_name = models.CharField(max_length=100)
    school_logo = models.ImageField(upload_to="logo")

    def __str__(self):
        return self.school_name
