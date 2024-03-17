from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, F, Count, Sum
from .models import (FormStreamYear, Student, Category, Row, Column, 
                     Book, Borrowed, Counter, Staff, School)
from .forms import FormStreamYearForm
from django.forms import modelformset_factory
from django.contrib import messages
from django.views.generic import ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import datetime
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import secrets
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator

@login_required 
def home(request):
    if request.user.is_classteacher:
        return redirect('class-teacher')

    
    elif request.user.is_librarian:
        categories = Category.objects.all()

        school = School.objects.all().first()

        context = {'categories': categories, 'school': school}

        return render(request, 'library/librarian.html', context)
    
    elif request.user.is_superuser:
        return redirect('admin:index')
        # return render(request, "library/no_content.html")
    
    else:
        raise PermissionDenied


@login_required 
@permission_required(['library.change_formstreamyear', 'library.add_student'], raise_exception=True)
def class_teacher(request):
    query = FormStreamYear.objects.filter(Q(teacher=request.user))
    obj = query.first()

    # Creating a class from the modelformset_factory
    StudentFormsetForm = modelformset_factory(Student, fields=['student_name', 'student_admission_no'], extra=5, can_delete=True)
    
    queryset = Student.objects.none()

    if request.method == "POST":
        form = FormStreamYearForm(request.POST, instance=obj)

        # Creating an object formset of the "StudentFormsetForm" class

        formset = StudentFormsetForm(request.POST)

        if form.is_valid():
            form.save()
            
            messages.success(request, "Class updated")
            return redirect('class-teacher')

        elif formset.is_valid():
            instances = formset.save(commit=False)

            for instance in instances:
                instance.form_stream_year = obj
                instance.save()

            
            for form_object in formset.deleted_objects:
                form_object.delete()
                
                return redirect('class-teacher')



    # Form object
    form = FormStreamYearForm(instance=obj)
    
    # Formset object
    formset = StudentFormsetForm(queryset=queryset)

    # Students
    students = Student.objects.filter(Q(form_stream_year=obj))


    # Details about the school
    school = School.objects.all().first()

    context = {'query': query, 'students': students, 'form': form, 'formset': formset, 'school': school}

    return render(request, 'library/teacher.html', context)



# View to register to a class
@login_required 
@permission_required('library.add_formstreamyear', raise_exception=True)
def register_class(request):
    if request.method == "POST":
        form_label = request.POST['label']
        stream = request.POST['stream']
        year = request.POST['year']

        if form_label and stream and year:
            FormStreamYear.objects.create(form_label=form_label, stream=stream, year=year, teacher=request.user)

            return redirect('class-teacher')

        messages.error(request, "Form incorrectly filled")
        return redirect('home')


# Class based view to remove student from the class
class StudentDeleteView(LoginRequiredMixin,PermissionRequiredMixin, DeleteView):
    model = Student
    permission_required = ['library.delete_student']

    def get_success_url(self):
        messages.success(self.request, "Student removed from the class")
        return reverse_lazy('class-teacher')


# View to update student name
@login_required 
@permission_required('library.change_student', raise_exception=True)
def update_student_name(request, **kwargs):
    student = get_object_or_404(Student, pk=kwargs['student_ID'])

    if request.method == "POST":
        update = request.POST['student']

        # Now updating the student name
        student.student_name = update
        student.save()

        messages.success(request, "Student name updated.")
        return redirect('class-teacher')



# View to display category/subject rows or forms
@login_required 
def category_rows(request, **kwargs):
    # Category object
    category = get_object_or_404(Category, pk=kwargs['category_ID'])

    # Category/Subject rows/forms
    rows = Row.objects.filter(Q(category=category)).order_by('shelve')

    # Categories/subjects
    categories = Category.objects.all()

    school = School.objects.all().first()

    context = {'categories': categories, 'rows': rows, 'category': category, 'school': school}

    return render(request, 'library/category_rows.html', context)


# View to display row columns and books
@login_required 
def row_columns(request, **kwargs):
    # Row instance/object
    row_object = get_object_or_404(Row, pk=kwargs.get('row_ID'))

    # Category/Subject rows/forms
    rows = Row.objects.filter(Q(category=row_object.category)).order_by('shelve')

    # Row columns
    columns = Column.objects.filter(Q(row=row_object)).order_by('column_name')

    # Dictionary object to hold row columns and there books
    columns_books = {}

    # Looping over the column queryset to find books attached to every column
    for column in columns:
        books = Book.objects.filter(Q(column=column)).order_by('book_serial_no')

        # Now attaching books to respective columns
        columns_books[column] = books

    
    # Categories/subjects
    categories = Category.objects.all()

    school = School.objects.all().first()

    
    context = {'row': row_object, 'row_books': columns_books, 'categories': categories,
                'rows': rows, 'category': row_object.category, 'school': school}
    return render(request, 'library/row_book.html', context)


# View to handle books to be given through the checkbox option
@login_required 
def checkbox_options(request):
    if request.method == "POST":
        # context = {'data': list(request.POST.values())}
        # return render(request, 'library/confirm.html', context)
        book_ids = []

        for k in request.POST:
            book_ids.append(request.POST[k])


        if len(book_ids) == 1:
            book = get_object_or_404(Book, pk=book_ids[0])

            return redirect('book-details', book.id)




# View to show the clicked book details
@login_required
def book_details(request, **kwargs):
    book = get_object_or_404(Book, pk=kwargs.get('book_ID'))

    # row instanced, traced using book instance then column instance
    row_object = book.column.row

    # Category/Subject rows/forms
    rows = Row.objects.filter(Q(category=row_object.category)).order_by('shelve')

    # Row columns
    columns = Column.objects.filter(Q(row=row_object)).order_by('column_name')

    # Dictionary object to hold row columns and there books
    columns_books = {}

    # Looping over the column queryset to find books attached to every column
    for column in columns:
        books = Book.objects.filter(Q(column=column)).order_by('book_serial_no')

        # Now attaching column its books
        columns_books[column] = books


    # Categories/subjects
    categories = Category.objects.all()

    school = School.objects.all().first()

    context = {'book': book, 'row_books': columns_books, 'categories': categories, 'rows': rows, 
               'category': row_object.category, 'row': row_object, 'school': school} 

    return render(request, 'library/book_details.html', context)



# View to handle bulk borrowing of books at once 

@login_required
def bulk_borrowing_view(request, **kwargs):
    # Column instance 
    column_obj = get_object_or_404(Column, pk=kwargs.get('column_ID'))

    # Category/Subject rows/forms
    rows = Row.objects.filter(Q(category=column_obj.row.category)).order_by('shelve')

    # Row columns
    columns = Column.objects.filter(Q(row=column_obj.row)).order_by('column_name')


    # Dictionary object to hold row columns and there books
    columns_books = {}

    # Looping over the column queryset to find books attached to every column
    for column in columns:
        books = Book.objects.filter(Q(column=column)).order_by('book_serial_no')

        # Now attaching column its books
        columns_books[column] = books

    col_books = Book.objects.filter(Q(column=column_obj))

    # List object to hold books not borrowed in a column
    col_non_borrowed_books = []

    for bk in col_books:
        book_queryset = Borrowed.objects.filter(Q(book=bk))

        if book_queryset.first():
            pass
        else:
            col_non_borrowed_books.append(bk)
            

    # Categories/subjects
    categories = Category.objects.all()

    school = School.objects.all().first()

    context = {'row_books': columns_books, 'categories': categories, 'rows': rows, 'column': column_obj,
               'category': column_obj.row.category, 'row': column_obj.row, 'books': col_non_borrowed_books,
                 'school': school}
    
    return render(request, 'library/bulk_borrow_page.html', context)



# View to accept data submitted from a form "Bulk borrowing"

@login_required 
def bulk_borrow_search_form_data(request, **kwargs):
    column = get_object_or_404(Column, pk=kwargs['column_ID'])

    if request.method == "POST":
        data = request.POST['reg_no']

        student_query = Student.objects.filter(Q(student_admission_no=data))

        staff_query = Staff.objects.filter(Q(staff_member_no=data))

        if student_query.first():
            x = '6'+'b1f43e'+str(student_query.first().student_admission_no)
            return redirect('find-matching-records', x, column.id)
        
        elif staff_query.first():
            y = '6'+'c1d7fb'+str(staff_query.first().staff_member_no)
            return redirect('find-matching-records', y, column.id)
        
        else:
            messages.error(request, "Something went wrong!")
            return redirect('bulk-borrowing', column.id)
        

# View to use submitted form data to find matching records

@login_required 
def find_matching_records(request, **kwargs):
    # Column instance of the Column model class
    column_object = get_object_or_404(Column, pk=kwargs.get('column_ID'))

    text = str(kwargs.get('text'))

    text_string = []


    for txt in text:
        text_string.append(txt)

    

    # First character of the string e.g. 6
    first_element = text_string[:1]


    # Token string e.g. 'b1f43e'
    token_string = text_string[1:7]

    # context = {'text_string': isinstance(int(first_element[0]), int)}

    # return render(request, 'library/confirm.html', context)

    

    if int(first_element[0]) == len(token_string):
        reg_no = text_string[7:]

        reg_no_string = ''

        for xters in reg_no:
            reg_no_string +=xters


        student_query = Student.objects.filter(Q(student_admission_no=reg_no_string))

        staff_query = Staff.objects.filter(Q(staff_member_no=reg_no_string))

        # A variable to hold either student instance or staff instance 
        instance = []

        # List object to hold either student reg no or staff reg no
        reg_no = []

        borrowing_status = []

        if student_query.first():
            student_b_status = Borrowed.objects.filter(Q(student=student_query.first())).order_by('date_borrowed')
            borrowing_status.append(student_b_status)

            instance.append(student_query.first())

            reg_no.append(student_query.first().student_admission_no)
        
        if staff_query.first():
            staff_b_status = Borrowed.objects.filter(Q(staff=staff_query.first())).order_by('date_borrowed')
            borrowing_status.append(staff_b_status)

            instance.append(staff_query.first())

            reg_no.append(staff_query.first().staff_member_no)

        
        # Category/Subject rows/forms
        rows = Row.objects.filter(Q(category=column_object.row.category)).order_by('shelve')

        # Row columns
        columns = Column.objects.filter(Q(row=column_object.row)).order_by('column_name')


        # Dictionary object to hold row columns and there books
        columns_books = {}

        # Looping over the column queryset to find books attached to every column

        for column in columns:
            books = Book.objects.filter(Q(column=column)).order_by('book_serial_no')

            # Now attaching column its books
            columns_books[column] = books





        col_books = Book.objects.filter(Q(column=column_object))

        # List iterable object to hold books not borrowed in a particular column

        col_non_borrowed_books = []

        for bk in col_books:
            book_queryset = Borrowed.objects.filter(Q(book=bk))

            if book_queryset.first():
                pass
            else:
                col_non_borrowed_books.append(bk)
            

        # Categories/subjects
        categories = Category.objects.all()

        school = School.objects.all().first()

        context = {'row_books': columns_books, 'categories': categories, 'rows': rows, 'status': borrowing_status,
                'category': column_object.row.category, 'row': column_object.row, 'books': col_non_borrowed_books, 
                'column': column_object, 'instance': instance, 'reg_no': reg_no, 'school': school}
        
        return render(request, 'library/find_matching_records.html', context)
    
    
    messages.error(request, "Something might have gone wrong")
    return redirect('find-matching-records', text, column_object.id)


        
# View to ensure the form data is saved to the database
@login_required
def save_bulk_data(request, **kwargs):
    
    if request.method == "POST":
        # Column model class instance
        column = get_object_or_404(Column, pk=kwargs.get('column_ID'))

        # Person's borrowing bulk books instance
        student_query = Student.objects.filter(Q(student_admission_no=kwargs.get('reg_no')))

        staff_query = Staff.objects.filter(Q(staff_member_no=kwargs.get('reg_no')))

        values = request.POST.getlist('book')


        # Current date (datetime object)
        today = datetime.datetime.today()

        # Using isocalender() method of the datetime object to get/find date week number
        week_num = today.isocalendar()[1]

        # Current date (date object)
        date = datetime.date(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day)

        
        for element in values:
            book = get_object_or_404(Book, pk=element)

            # Counter model class objects ordered from the latest to the oldest
            counters = Counter.objects.all().order_by('-date')

            if student_query.first():
                Borrowed.objects.create(book=book, student=student_query.first(), librarian=request.user)

                if counters:
                    # date object "latest_count_date"
                    latest_count_date = datetime.date(counters.first().date.year, counters.first().date.month, counters.first().date.day)

                    if latest_count_date == date:
                        counters.first().counts = F('counts') + 1
                        counters.first().save()

                    else:
                        Counter.objects.create(counts=1, week_num=week_num)

                else:
                    Counter.objects.create(counts=1, week_num=week_num)

            else:
                Borrowed.objects.create(book=book, staff=staff_query.first(), librarian=request.user)

                if counters:
                    # date object "latest_count_date"
                    latest_count_date = datetime.date(counters.first().date.year, counters.first().date.month, counters.first().date.day)

                    if latest_count_date == date:
                        counters.first().counts = F('counts') + 1
                        counters.first().save()
                    else:
                        Counter.objects.create(counts=1, week_num=week_num)

                else:
                    Counter.objects.create(counts=1, week_num=week_num)


        return redirect('bulk-borrowing', column.id)

    

# Search for the student instance view
@login_required 
def search_student(request, **kwargs):
    # Book object
    book_object = get_object_or_404(Book, pk=kwargs.get('book_ID'))

    if request.method == "POST":
        student_admission_no = request.POST['adm_no']

        # Student instance
        student_object_query = Student.objects.filter(Q(student_admission_no=student_admission_no)) 

        if student_object_query:
            return redirect('search-output', student_object_query.first().id, book_object.id)

        messages.error(request, "Student's admission number incorrect")
        return redirect('book-details', book_object.id)

    




# View to show student book borrowing records if are there and the link to give a student a book
@login_required 
def search_output(request, **kwargs):
    # Student object
    student = get_object_or_404(Student, pk=kwargs.get('student_ID'))

    # Book object
    book = get_object_or_404(Book, pk=kwargs.get('book_ID'))

    # row instanced traced using book instance then column instance
    row_object = book.column.row

    # Category/Subject rows/forms
    rows = Row.objects.filter(Q(category=row_object.category)).order_by('shelve')

    # Row columns
    columns = Column.objects.filter(Q(row=row_object)).order_by('column_name')

    # Dictionary object to hold row columns and there books
    columns_books = {}

    # Looping over the column queryset to find books attached to every column
    for column in columns:
        books = Book.objects.filter(Q(column=column)).order_by('book_serial_no')

        # Now attaching column its books
        columns_books[column] = books


    # Categories/subjects
    categories = Category.objects.all()

    school = School.objects.all().first()

    # Student's borrowing records
    records = Borrowed.objects.filter(Q(student=student)).order_by('date_borrowed')

    context = {'student': student, 'book': book, 'records': records, 'row_books': columns_books,
               'categories': categories, 'rows': rows, 'category': row_object.category, 'row': row_object,
                 'school': school}

    return render(request, 'library/search_output.html', context)


# View to execute giving out of a book to a student
@login_required
def give_out_the_book(request, **kwargs):
    # Student instance
    student = get_object_or_404(Student, pk=kwargs.get('student_ID'))

    # Current date (datetime object)
    today = datetime.datetime.today()

    # Using isocalender() method of the datetime object to get/find date week number
    week_num = today.isocalendar()[1]

    # Current date (date object)
    date = datetime.date(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day)

    # Counter model class objects ordered from the latest to the oldest
    counters = Counter.objects.all().order_by('-date')

    # Book instance 
    book = get_object_or_404(Book, pk=kwargs.get('book_ID'))

    # Capturing the borrowed book details
    Borrowed.objects.create(book=book, student=student, librarian=request.user)

    if counters:
        # date object "latest_count_date"
        latest_count_date = datetime.date(counters.first().date.year, counters.first().date.month, counters.first().date.day)

        if latest_count_date == date:
            counters.first().counts = F('counts') + 1
            counters.first().save()

            return redirect('search-output', student.id, book.id)

        Counter.objects.create(counts=1, week_num=week_num)
        return redirect('search-output', student.id, book.id)

    Counter.objects.create(counts=1, week_num=week_num)
    return redirect('search-output', student.id, book.id)


# Search staff member instance 
@login_required 
def search_staff_member(request, **kwargs):
    # Book object
    book_object = get_object_or_404(Book, pk=kwargs.get('book_ID'))

    if request.method == "POST":
        staff_member_no = request.POST['staff_member_no']

        # Student instance
        staff_object_query = Staff.objects.filter(Q(staff_member_no=staff_member_no)) 

        if staff_object_query:
            return redirect('search-finding', staff_object_query.first().id, book_object.id)

        messages.error(request, "Staff member number incorrect")
        return redirect('book-details', book_object.id)


# Search findings related to a staff member
@login_required
def search_findings(request, **kwargs):
     # Student object
    staff = get_object_or_404(Staff, pk=kwargs.get('staff_member_ID'))

    # Book object
    book = get_object_or_404(Book, pk=kwargs.get('book_ID'))

    # row instanced traced using book instance then column instance
    row_object = book.column.row

    # Category/Subject rows/forms
    rows = Row.objects.filter(Q(category=row_object.category)).order_by('shelve')

    # Row columns
    columns = Column.objects.filter(Q(row=row_object)).order_by('column_name')

    # Dictionary object to hold row columns and there books
    columns_books = {}

    # Looping over the column queryset to find books attached to every column
    for column in columns:
        books = Book.objects.filter(Q(column=column)).order_by('book_serial_no')

        # Now attaching column its books
        columns_books[column] = books


    # Categories/subjects
    categories = Category.objects.all()

    school = School.objects.all().first()

    # Staff member's borrowing records
    records = Borrowed.objects.filter(Q(staff=staff)).order_by('date_borrowed')

    context = {'staff': staff, 'book': book, 'records': records, 'row_books': columns_books,
               'categories': categories, 'rows': rows, 'category': row_object.category, 'row': row_object, 'school': school}

    return render(request, 'library/search_findings.html', context)


# View to execute giving out of the book to the staff member 
@login_required 
def give_staff_member_the_book(request, **kwargs):
    # Student instance
    staff = get_object_or_404(Staff, pk=kwargs.get('staff_member_ID'))

    # Current date (datetime object)
    today = datetime.datetime.today()

    # Using isocalender() method of the datetime object to get/find date week number
    week_num = today.isocalendar()[1]

    # Current date (date object)
    date = datetime.date(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day)

    # Counter model class objects ordered from the latest to the oldest
    counters = Counter.objects.all().order_by('-date')

    # Book instance 
    book = get_object_or_404(Book, pk=kwargs.get('book_ID'))

    # Capturing the borrowed book details
    Borrowed.objects.create(book=book, staff=staff, librarian=request.user)

    if counters:
        # date object "latest_count_date"
        latest_count_date = datetime.date(counters.first().date.year, counters.first().date.month, counters.first().date.day)

        if latest_count_date == date:
            counters.first().counts = F('counts') + 1
            counters.first().save()

            return redirect('search-finding', staff.id, book.id)

        Counter.objects.create(counts=1, week_num=week_num)
        return redirect('search-finding', staff.id, book.id)

    Counter.objects.create(counts=1, week_num=week_num)
    return redirect('search-finding', staff.id, book.id)


# A view function to render a list of borrowed books

@login_required 
def list_of_borrowed_books(request):
    books = Borrowed.objects.all().order_by('-date_borrowed')

    paginator = Paginator(books, 3)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)


    # Current date
    today = datetime.datetime.today()

    # Week number
    week_num = today.isocalendar()[1]

    # Dictionary object
    weekday_instances = {}

    # Sum of books borrowed in a particular week
    total = Counter.objects.filter(Q(week_num=week_num)).aggregate(total_books=Sum('counts'))


    # Counter model class instance or objects for the current week of the year
    counters = Counter.objects.filter(Q(week_num=week_num)).order_by('date')


    # Looping over the Counter model class objects/instances
    for counter in counters:
        datetime_object = datetime.datetime(counter.date.year, counter.date.month, counter.date.day, 
                                            counter.date.hour, counter.date.minute, counter.date.second)

        # Week day in english
        weekday = datetime_object.strftime("%A")


        weekday_instances[weekday] = counter

    # A bout school info
    school = School.objects.all().first()

    context = {'counts': weekday_instances, 'week': week_num, 'page_obj': page_obj, 
               'total': total['total_books'], 'school': school}
    
    return render(request, 'library/borrowed_list.html', context)



# Class based View to render all borrowed books details
class BorrowedBooksListView(LoginRequiredMixin, ListView):
    model = Borrowed
    context_object_name = 'books'
    ordering = ['-date_borrowed']
    paginate_by = 3


    def get_context_data(self, **kwargs):
        # Current date
        today = datetime.datetime.today()

        # Week number
        week_num = today.isocalendar()[1]

        # Dictionary object
        weekday_instances = {}

        # Sum of books borrowed in a particular week
        total = Counter.objects.filter(Q(week_num=week_num)).aggregate(total_books=Sum('counts'))


        # Counter model class instance or objects for the current week of the year
        counters = Counter.objects.filter(Q(week_num=week_num)).order_by('date')


        # Looping over the Counter model class objects/instances
        for counter in counters:
            datetime_object = datetime.datetime(counter.date.year, counter.date.month, counter.date.day, 
                                                counter.date.hour + 3, counter.date.minute, counter.date.second)

            # Week day in english
            weekday = datetime_object.strftime("%A")


            weekday_instances[weekday] = counter

        # A bout school info
        school = School.objects.all().first()


        kwargs['counts'] = weekday_instances
        kwargs['week'] = week_num
        kwargs['total'] = total['total_books']
        kwargs['school'] = school 
        
        # Return the context data to the class
        return super().get_context_data(**kwargs)
    

# View to print books borrowed by the students 
@login_required
def print_books_borrowed(request):
    books = Borrowed.objects.all().order_by('date_borrowed')

    # Details about the school
    school = School.objects.all().first()

    template_path = "library/print_books_borrowed.html"

    context = {'books': books, 'school': school}

    response = HttpResponse(content_type="application/pdf")

    response['Content-Disposition'] = "filename=list_of_books_borrowed.pdf"

    template = get_template(template_path)

    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Something went wrong')
    
    return response


# View to pass a student admission number in search of borrowed books records
@login_required 
def student_and_staff_reg_no(request):
    if request.method == "POST":
        reg_no = request.POST['reg_no']

        # Looking for the student instance using the student's reg number
        student_query = Student.objects.filter(Q(student_admission_no=reg_no))


        # Looking for the staff member instance using the staff member's reg number
        staff = Staff.objects.filter(Q(staff_member_no=reg_no))

        if student_query:
            registration_no = str(student_query.first().id)+"?"+str(student_query.first().student_admission_no)
            return redirect('unreturned-borrowed-books', registration_no)

        elif staff:
            registration_no = str(staff.first().id)+"?"+str(staff.first().staff_member_no)
            return redirect('unreturned-borrowed-books', registration_no)

        else:
            messages.error(request, "Incorrect registration number, Double check.")
            return redirect('borrowed-books')


# View to find student's unreturned borrowed books records
@login_required
def unreturned_borrowed_books_details(request, **kwargs):
    object_id, reg_no = kwargs.get('reg_no').split('?')

    # Student queryset
    student_query = Student.objects.filter(Q(id__exact=object_id), Q(student_admission_no=reg_no))


    # Staff member queryset
    staff = Staff.objects.filter(Q(id__exact=object_id), Q(staff_member_no=reg_no))

    # student = get_object_or_404(Student, pk=kwargs.get('student_ID'))


    # Queryset for unreturned borrowed books for the student
    # details = Borrowed.objects.filter(Q(student=student)).order_by('-date_borrowed')


    # Querset of unreturned borrowed books
    books = Borrowed.objects.all().order_by('-date_borrowed')

    # Paginating the books queryset to get three books per page

    paginator = Paginator(books, 3)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)


    # A logic on finding counts on how books are borrowed daily in the library


    # Current date
    today = datetime.datetime.today()

    # Week number
    week_num = today.isocalendar()[1]

    # Dictionary object
    weekday_instances = {}

    # Sum of books borrowed in a particular week
    total = Counter.objects.filter(Q(week_num=week_num)).aggregate(total_books=Sum('counts'))

    # Counter model class instance or objects for the current week of the year
    counters = Counter.objects.filter(Q(week_num=week_num)).order_by('date')

    # Looping over the Counter model class objects/instances
    for counter in counters:
        datetime_object = datetime.datetime(counter.date.year, counter.date.month, counter.date.day, 
                                            counter.date.hour, counter.date.minute, counter.date.second)

        # Week day in english
        weekday = datetime_object.strftime("%A")


        weekday_instances[weekday] = counter

    
    # Info about school
    school = School.objects.all().first()

    
    if student_query:
        # Queryset for unreturned borrowed books for the student
        details = Borrowed.objects.filter(Q(student=student_query.first())).order_by('-date_borrowed')

        context = {'student': student_query.first(), 'unreturned_books': details, 'books': books,
                    'counts': weekday_instances, 'week': week_num, 'total': total['total_books'],
                      'school': school, 'page_obj': page_obj}

        return render(request, 'library/unreturned_books_details.html', context)
    
    elif staff:
        # Queryset for unreturned borrowed books by the staff member
        details = Borrowed.objects.filter(Q(staff=staff.first())).order_by('-date_borrowed')

        context = {'staff': staff.first(), 'unreturned_books': details, 'books': books,
                   'counts': weekday_instances, 'week': week_num, 'school': school,
                     'total': total['total_books'], 'page_obj': page_obj}

        return render(request, 'library/unreturned_books_details.html', context)



# View to receive and delete student's borrowed book details
@login_required
def delete_borrowed_book_record(request, **kwargs):
    # Borrowed book record to be deleted
    book_record = get_object_or_404(Borrowed, pk=kwargs.get('book_record_ID'))

    # Student instance 
    # student = get_object_or_404(Student, pk=kwargs.get('student_ID'))

    # Student queryset
    student_query = Student.objects.filter(Q(id__exact=kwargs.get('object_ID')), Q(student_admission_no=kwargs['reg_no']))


    # Staff member queryset
    staff = Staff.objects.filter(Q(id__exact=kwargs.get('object_ID')), Q(staff_member_no=kwargs['reg_no']))

    if request.method == "POST":

        if student_query:
            # Delete a borrowed book record by calling delete method of the object/instance
            book_record.delete()

            registration_no = str(student_query.first().id)+"?"+str(student_query.first().student_admission_no)
            return redirect('unreturned-borrowed-books', registration_no)
        
        elif staff:
            # Delete a borrowed book record by calling delete method of the object/instance
            book_record.delete()

            registration_no = str(staff.first().id)+"?"+str(staff.first().staff_member_no)
            return redirect('unreturned-borrowed-books', registration_no)
        
        
    
    if student_query:
        registration_no = str(student_query.first().id)+"?"+str(student_query.first().student_admission_no)
        context = {'reg_no': registration_no}
        return render(request, 'library/borrowed_confirm_delete.html', context)

    elif staff:
        registration_no = str(staff.first().id)+"?"+str(staff.first().staff_member_no)
        context = {'reg_no': registration_no}
        return render(request, 'library/borrowed_confirm_delete.html', context)


# View to show book search page
@login_required
def search_book_info_page(request):
    return render(request, 'library/search_book_info_page.html')
    

# View to perform book search info
@login_required 
def search_book_info(request):
    if request.method == "POST":
        book_query = Book.objects.filter(Q(book_serial_no=request.POST['serial_no']))

        if book_query:
            return redirect('book-info', book_query.first().id)
        
        messages.error(request, "The book and it's info doesn't exist")
        return redirect('search-book-info-page')



# View to show book details/info and/or details if the book is currently borrowed
@login_required
def book_info(request, **kwargs):
    # Book object
    book = get_object_or_404(Book, pk=kwargs.get('book_ID'))

    # Book details if its currently borrowed
    data = Borrowed.objects.filter(Q(book=book)).first()

    context = {'book_info': book, 'data': data}

    return render(request, 'library/book_info.html', context)