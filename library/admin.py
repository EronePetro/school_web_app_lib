from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin, ExportActionModelAdmin
# from django.urls import reverse
# from django.utils.html import format_html
from import_export.fields import Field
from .models import (Category, Row, Column, Book, Borrowed, 
                     FormStreamYear, Student, Counter, Staff,
                     School)

admin.site.register(Category)

class RowAdmin(admin.ModelAdmin):
    list_display = ['shelve', 'category']
    list_select_related = ['category']

    # def display_category(self, obj):
        # link = reverse('admin: library_category_change', args=[obj.category.id])
        # return format_html('<a href="{}">{}<a/>', link, obj.category)
    
    # display_category.short_description = "category"
    search_fields = ['shelve', 'category__category_name']

admin.site.register(Row, RowAdmin)

class ColumnAdmin(admin.ModelAdmin):
    list_display = ['column_name', 'row']
    list_select_related = ['row']

    search_fields = ['column_name', 'row__shelve']


admin.site.register(Column, ColumnAdmin)

class BookAdmin(admin.ModelAdmin):
    list_display = ['book_serial_no', 'book_name', 'column']
    list_select_related = ['column']

    list_filter = ['book_serial_no', 'book_name']

    search_fields = ['book_serial_no', 'book_name']

admin.site.register(Book, BookAdmin)

# Model resources for Borrowed model class
class BorrowedResource(resources.ModelResource):
    book_serial = fields.Field(attribute='book__book_serial_no')
    book_name = fields.Field(attribute='book__book_name')
    student_reg_no = fields.Field(attribute='student__student_admission_no')
    student_name = fields.Field(attribute='student__student_name')
    staff_reg_no = fields.Field(attribute='staff__staff_member_no')
    staff_member_name = fields.Field(attribute='staff__staff_member_name')
    librarian = fields.Field(attribute='librarian__full_name')

    class Meta:
        model = Borrowed
        fields = ['book_serial', 'book_name', 'student_reg_no', 'student_name',
                   'staff_reg_no', 'staff_member_name', 'librarian', 'date_borrowed']
        
        export_order = fields


class BorrowedAdmin(ExportActionModelAdmin):
    list_display = ['book', 'student', 'staff', 'librarian', 'date_borrowed']
    list_select_related = ['book', 'student', 'staff', 'librarian']

    search_fields = ['book__book_name', 'student__student_admission_no', 'student__student_name',
                      'staff__staff_member_no', 'staff__staff_member_name', 'librarian__full_name']
    
    resource_classes = [BorrowedResource]

admin.site.register(Borrowed, BorrowedAdmin)

class FormStreamYearAdmin(admin.ModelAdmin):
    list_display = ['form_label', 'stream', 'year', 'teacher']
    list_select_related = ['teacher']

admin.site.register(FormStreamYear, FormStreamYearAdmin)


# Model resource for the student model class

class StudentResource(resources.ModelResource):
    student_admission_no = Field(attribute='student_admission_no', column_name='Reg_no')
    form_label = fields.Field(attribute='form_stream_year__form_label')
    stream = fields.Field(attribute='form_stream_year__stream')
    year = fields.Field(attribute='form_stream_year__year')
    class_teacher = fields.Field(attribute='form_stream_year__teacher__full_name')


    class Meta:
        model = Student
        # use_natural_foreign_keys = True
        fields = [
                  'student_admission_no', 'student_name', 'form_label', 
                  'stream', 'year', 'class_teacher'
                  ]
        export_order = fields
        

class StudentAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    list_display = ['student_admission_no', 'student_name', 'form_stream_year']
    list_select_related = ['form_stream_year', 'form_stream_year__teacher']

    list_filter = ['student_admission_no', 'student_name']

    search_fields = ['student_admission_no', 'student_name', 'form_stream_year__form_label', 'form_stream_year__stream', 
                     'form_stream_year__year', 'form_stream_year__teacher__full_name']
    
    resource_classes = [StudentResource]

admin.site.register(Student, StudentAdmin)



# ModelAdmin for the counter model class

class CounterAdmin(admin.ModelAdmin):
    list_display = ['counts', 'week_num', 'date']
    search_fields = ['counts', 'week_num', 'date']

admin.site.register(Counter, CounterAdmin)

class StaffAdmin(admin.ModelAdmin):
    list_display = ['staff_member_no', 'staff_member_name', 'contact']
    search_fields = ['staff_member_no', 'staff_member_name', 'contact']

admin.site.register(Staff, StaffAdmin)

class SchoolAdmin(admin.ModelAdmin):
    list_display = ['school_name', 'school_logo']

admin.site.register(School, SchoolAdmin)