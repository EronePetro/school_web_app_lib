from django.test import TestCase, tag
from django.contrib.auth import get_user_model
from django.urls import reverse
from .views import class_teacher, StudentDeleteView, book_details, search_output, BorrowedBooksListView, delete_borrowed_book_record
from .models import Student, FormStreamYear, Category, Row, Column, Book, Borrowed
from django.utils import timezone

@tag('class-teacher')
class ClassTeacherTestCase(TestCase):
    # To access the class teacher view, you must have an account and logged in
    def test_class_teacher_view_with_user(self):
        # Creating user account
        get_user_model().objects.create_user("Patric Omella", "omellapatric@gmail.com", "petro77??")

        # Logging in the user with the account using the login() method of the test client
        response = self.client.login(email="omellapatric@gmail.com", password="petro77??")

        self.assertTrue(response)

        # Response for accessing the class teacher page
        response_1 = self.client.get(reverse('class-teacher'))

        self.assertEqual(response_1.status_code, 200)

        self.assertEqual(response_1.resolver_match.func, class_teacher)


    @tag('non-logged')
    def test_class_teacher_view_access_by_non_logged_in_users(self):
        # User account 
        get_user_model().objects.create_user("Vivian Papa", "papavivian@gmail.com", "petro77??")

        # Accesing the class teacher view without logging into the system
        response = self.client.get(reverse('class-teacher'))

        self.assertEqual(response.status_code, 302)
        
        # Testing for redirect to the login page if not logged in while accessing the page the demands login first
        self.assertRedirects(response, "/accounts/login/?next=/class-teacher/")

@tag('register-class')
class RegisterClassTestCase(TestCase):
    def test_class_registration(self):
        # Creating user account 
        get_user_model().objects.create_user("Allan Ken", "kenallan@gmail.com", "petro77??")

        # Logging in the user
        response = self.client.login(email="kenallan@gmail.com", password="petro77??")

        # Checking for the response 
        self.assertTrue(response)


# Method to create FormStreamYear test instance
def create_form_stream_year(label, stream, year, teacher):
    return FormStreamYear.objects.create(form_label=label, stream=stream, year=year, teacher=teacher)

# Function to create student test instance
def create_student(reg_no, student_name, fsy):
    return Student.objects.create(student_admission_no=reg_no, student_name=student_name, form_stream_year=fsy)


# Testcase to test for the student removal from the class
@tag('student_removal')
class DeleteStudentTests(TestCase):
    def test_student_removal_in_a_class(self):
        # Teacher's instance 
        teacher = get_user_model().objects.create_user(full_name="Sam Kamau", email="kamausam@gmail.com", is_classteacher="True", password="petro77??")
        
        # Logging in the class teacher
        self.client.login(email="kamausam@gmail.com", password="petro77??")

        # form_stream_year instance
        form_stream_year = create_form_stream_year(label=1, stream="White", year=2023, teacher=teacher)

        # Student instance
        student = create_student(reg_no="W-2023", student_name="Joshua Odilo", fsy=form_stream_year)

        url = reverse('remove-student', args=(student.id,))


        # Get request on the url
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure you want to remove the student from your class.")
        self.assertEqual(response.resolver_match.func.__name__, StudentDeleteView.as_view().__name__)
        self.assertTemplateUsed(response, "library/student_confirm_delete.html")


# Method that creates Category test instance
def create_category(name):
    return Category.objects.create(category_name=name)

# Method to create Row model class test instance
def create_row(name, category):
    return Row.objects.create(shelve=name, category=category)
    
# TestCase to test for category rows access
@tag('category_rows')
class CategoryRowsTests(TestCase):
    @tag('rows')
    def test_category_rows_access(self):
        # Librarian account creation
        get_user_model().objects.create_user(full_name="Broline Ngaina", email="ngainabroline@gmail.com", is_librarian="True", password="petro77??")

        # Librarian login
        self.client.login(email="ngainabroline@gmail.com", password="petro77??")

        # Category instance creation
        category = create_category(name="Maths")

        # Create rows/shelves test instance for category
        row = create_row(name="1", category=category)
        row1 = create_row(name="2", category=category)
        row2 = create_row(name="3", category=category)

        response = self.client.get(reverse('category', args=(category.id,)))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['rows'], [row, row1, row2])
        self.assertEqual(len(response.context['rows']), 3)
        self.assertEqual(response.context['category'], category)

    @tag('no_rows')
    def test_no_category_rows(self):
        # Librarian account creation
        get_user_model().objects.create_user(full_name="Broline Ngaina", email="ngainabroline@gmail.com", is_librarian="True", password="petro77??")

        # Librarian login
        self.client.login(email="ngainabroline@gmail.com", password="petro77??")

        # Category instance creation
        category = create_category(name="Maths")
        
        # An HttpResponse object
        response = self.client.get(reverse('category', args=(category.id,)))

        self.assertQuerysetEqual(response.context['rows'], [])
        self.assertEqual(response.context['category'], category)

# Method to create column test instances
def create_column(name, row):
    return Column.objects.create(column_name=name, row=row)


# Method to create Book test instance
def create_book(serial_no, name, column):
    return Book.objects.create(book_serial_no=serial_no, book_name=name, column=column)

    
# TestCase to test row columns
@tag('row_columns')
class RowColumnTests(TestCase):
    def test_row_columns_and_books(self):
        # Librarian account creation
        get_user_model().objects.create_user(full_name="Broline Ngaina", email="ngainabroline@gmail.com", is_librarian="True", password="petro77??")

        # Librarian login
        self.client.login(email="ngainabroline@gmail.com", password="petro77??")

        # Category instance creation
        category = create_category(name="Maths")

        # Create row/shelve test instance for category
        row = create_row(name="1", category=category)

        # Row columns 
        column = create_column(name="A", row=row)
        column1 = create_column(name="B", row=row)
        column2 = create_column(name="C", row=row)

        # 1st Column books
        book = create_book(serial_no="M-123", name="KLB Maths", column=column)
        book1 = create_book(serial_no="M-124", name="KLB Maths", column=column)

        # 2nd column books
        book2 = create_book(serial_no="M-125", name="Made Familiar Maths", column=column1)
        book3 = create_book(serial_no="M-126", name="Made Familiar Maths", column=column1)

        # 3rd column books
        book4 = create_book(serial_no="M-127", name="Mirror Maths", column=column2)
        book5 = create_book(serial_no="M-128", name="Mirror Maths", column=column2)

        a = {column:[book, book1], column1:[book2, book3], column2:[book4, book5]}

        response = self.client.get(reverse('row-columns-books', args=(row.id,)))

        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.context['row_books'], a)


@tag('book-details')
class BookDetailsTests(TestCase):
    def test_presence_of_book_details(self):
        get_user_model().objects.create_user("Thomas Juma", "jumathomas@gmail.com", "petro77??")

        # Log in the user
        self.client.login(email="jumathomas@gmail.com", password="petro77??")

        category = create_category(name="English")

        row = create_row(name="Form 4", category=category)

        column = create_column(name="USAID English -  A", row=row)

        book = create_book(serial_no="E4-100", name="USAID English", column=column)

        response = self.client.get(reverse('book-details', args=(book.id,)))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/book_details.html')
        self.assertEqual(response.resolver_match.func, book_details)
        self.assertEqual(response.context['book'], book)


def add_borrowed_book(book, student, librarian):
    return Borrowed.objects.create(book=book, date_borrowed=timezone.now(), student=student, librarian=librarian)


@tag('borrowed-books')
class BorrowedBooksTests(TestCase):
    def test_student_borrowed_books(self):
        # Librarian test object/instance
        librarian = get_user_model().objects.create_user("Faith Atoo", "atoofaith@gmail.com", "petro77??")

        # Logging in the librarian
        self.client.login(email="atoofaith@gmail.com", password="petro77??")

        # Teacher's test object
        teacher = get_user_model().objects.create_user("Edwin Opuko", "opukoedwin@gmail.com", "petro77??")

        # For stream year test instance  label, stream, year, teacher
        form_stream_object = create_form_stream_year(label=4, stream="White", year=2023, teacher=teacher)

        # Student's test instance/object
        student = create_student(reg_no="W-1234", student_name="Pauline Ekesa", fsy=form_stream_object)

        # Category test instances
        category_1 = create_category(name="Chemistry")

        category_2 = create_category(name="Biology")

        # Row test instances
        row_1 = create_row(name="Form 4", category=category_1)

        row_2 = create_row(name="Form 4", category=category_2)

        # Column test instances
        column_1 = create_column(name="KLB Chemistry - A", row=row_1)

        column_2 = create_column(name="Made Familiar Biology - C", row=row_2)


        # Book test instances
        book_1 = create_book(serial_no="C-1020", name="KLB Chemistry", column=column_1)
        
        book_2 = create_book(serial_no="B-2020", name="Made Familiar Biology", column=column_2)

        
        # Borrowed books test instances
        borrow_1 = add_borrowed_book(book=book_1, student=student, librarian=librarian)

        borrow_2 = add_borrowed_book(book=book_2, student=student, librarian=librarian)

        # Make a GET request 
        url = reverse('search-output', args=(student.id, book_1.id))
        
        response = self.client.get(url)

        # Calling assertion methods
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['book'], book_1)

        self.assertQuerysetEqual(response.context['records'], [borrow_1, borrow_2])

        self.assertTemplateUsed(response, 'library/search_output.html')

        self.assertEqual(response.resolver_match.func, search_output)

    @tag('no-book-borrowed')
    def test_no_book_borrowed_by_student(self):
         # Librarian test object/instance
        librarian = get_user_model().objects.create_user("Faith Atoo", "atoofaith@gmail.com", "petro77??")

        # Logging in the librarian
        self.client.login(email="atoofaith@gmail.com", password="petro77??")

        # Teacher's test object
        teacher = get_user_model().objects.create_user("Edwin Opuko", "opukoedwin@gmail.com", "petro77??")

        # For stream year test instance  label, stream, year, teacher
        form_stream_object = create_form_stream_year(label=4, stream="White", year=2023, teacher=teacher)

        # Student's test instance/object
        student = create_student(reg_no="W-1234", student_name="Pauline Ekesa", fsy=form_stream_object)

        # Category test instances
        category_1 = create_category(name="Chemistry")

        category_2 = create_category(name="Biology")

        # Row test instances
        row_1 = create_row(name="Form 4", category=category_1)

        row_2 = create_row(name="Form 4", category=category_2)

        # Column test instances
        column_1 = create_column(name="KLB Chemistry - A", row=row_1)

        column_2 = create_column(name="Made Familiar Biology - C", row=row_2)


        # Book test instances
        book_1 = create_book(serial_no="C-1020", name="KLB Chemistry", column=column_1)
        
        book_2 = create_book(serial_no="B-2020", name="Made Familiar Biology", column=column_2)

        
        # Borrowed books test instances
        # borrow_1 = add_borrowed_book(book=book_1, student=student, librarian=librarian)

        # borrow_2 = add_borrowed_book(book=book_2, student=student, librarian=librarian)

        # Make a GET request 
        url = reverse('search-output', args=(student.id, book_1.id))
        
        response = self.client.get(url)

        # Calling assertion methods
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['book'], book_1)

        self.assertQuerysetEqual(response.context['records'], [])


@tag('borrowed-books-list')
class BorrowedBooksTests(TestCase):
    def test_for_borrowed_books(self):
        # Librarian test object/instance
        librarian = get_user_model().objects.create_user("Faith Atoo", "atoofaith@gmail.com", "petro77??")

        # Logging in the librarian
        self.client.login(email="atoofaith@gmail.com", password="petro77??")

        # Teachers test object
        teacher_1 = get_user_model().objects.create_user("Edwin Opuko", "opukoedwin@gmail.com", "petro77??")

        teacher_2 = get_user_model().objects.create_user("Paul Oswan", "oswanpaul@gmail.com", "petro77??")

        # For stream year test instance  label, stream, year, teacher
        form_stream_object_1 = create_form_stream_year(label=1, stream="White", year=2023, teacher=teacher_1)

        # For stream year test instance  label, stream, year, teacher
        form_stream_object_2 = create_form_stream_year(label=2, stream="Blue", year=2023, teacher=teacher_2)

        # Students test instance/object
        student_1 = create_student(reg_no="W-1234", student_name="Pauline Ekesa", fsy=form_stream_object_1)

        # Student's test instance/object
        student_2 = create_student(reg_no="W-1235", student_name="Jackline Osiba", fsy=form_stream_object_2)

        # Category test instances
        category_1 = create_category(name="Chemistry")

        category_2 = create_category(name="Biology")

        # Row test instances
        row_1 = create_row(name="Form 1", category=category_1)

        row_2 = create_row(name="Form 2", category=category_2)

        # Column test instances
        column_1 = create_column(name="KLB Chemistry - A", row=row_1)

        column_2 = create_column(name="Made Familiar Biology - C", row=row_2)


        # Book test instances
        book_1 = create_book(serial_no="C-1020", name="KLB Chemistry", column=column_1)
        
        book_2 = create_book(serial_no="B-2020", name="Made Familiar Biology", column=column_2)

        
        # Borrowed books test instances
        borrow_1 = add_borrowed_book(book=book_1, student=student_1, librarian=librarian)

        borrow_2 = add_borrowed_book(book=book_2, student=student_2, librarian=librarian)

        # Make a GET request 
        url = reverse('borrowed-books')
        
        response = self.client.get(url)

        # Calling assertion methods
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context['books']), 2)

        self.assertQuerysetEqual(response.context['books'], [borrow_1, borrow_2])

        self.assertTemplateUsed(response, 'library/borrowed_list.html')

        self.assertEqual(response.resolver_match.func.__name__, BorrowedBooksListView.as_view().__name__)

    
    @tag('none-borrowed')
    def test_for_none_book_has_been_borrowed(self):
        get_user_model().objects.create_user("Nyosh Bosire", "bosirenyosh@gmail.com", "petro77??")

        # Logging in the librarian
        self.client.login(email="bosirenyosh@gmail.com", password="petro77??")

        response = self.client.get(reverse('borrowed-books'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['books'], [])
        self.assertContains(response, "No records for borrowed books")



@tag('unreturned-books')
class StudentUnreturnedBooksTests(TestCase):
    def test_student_unreturned_books(self):
        librarian = get_user_model().objects.create_user("Faith Juma", "jumafaith@gmail.com", "petro77??")

        # Logging in the librarian 
        self.client.login(email="jumafaith@gmail.com", password="petro77??")

        # Category test instances 
        category = create_category(name="Physics")

        row = create_row(name="Form 3", category=category)

        column = create_column(name="KLB Physics Book 3 - A", row=row)

        book = create_book(serial_no="P3-300", name="KLB Physics", column=column)

        teacher = get_user_model().objects.create_user("Eunice Okame", "okameeunice@gmail.com", "petro77??")

        form_stream_year = create_form_stream_year(label=3, stream="Green", year=2023, teacher=teacher)

        student = create_student(reg_no="G-1235", student_name="Lameck Muzungu", fsy=form_stream_year)

        unreturned_borrowed_book = add_borrowed_book(book=book, student=student, librarian=librarian)

        data = str(student.id)+"?"+student.student_admission_no

        url = reverse('unreturned-borrowed-books', args=(data,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertQuerysetEqual(response.context['unreturned_books'], [unreturned_borrowed_book])

@tag('return-borrowed-book')
class ReturnBorrowedBookTests(TestCase):
    def test_return_borrowed_book(self):
        librarian = get_user_model().objects.create_user("Faith Juma", "jumafaith@gmail.com", "petro77??")

        # Logging in the librarian 
        self.client.login(email="jumafaith@gmail.com", password="petro77??")

        # Category test instances 
        category = create_category(name="Physics")

        row = create_row(name="Form 3", category=category)

        column = create_column(name="KLB Physics Book 3 - A", row=row)

        book = create_book(serial_no="P3-300", name="KLB Physics", column=column)

        teacher = get_user_model().objects.create_user("Eunice Okame", "okameeunice@gmail.com", "petro77??")

        form_stream_year = create_form_stream_year(label=3, stream="Green", year=2023, teacher=teacher)

        student = create_student(reg_no="G-1235", student_name="Lameck Muzungu", fsy=form_stream_year)

        unreturned_borrowed_book = add_borrowed_book(book=book, student=student, librarian=librarian)

        url = reverse('delete-borrowed-book-record', args=(book.id, student.id, student.student_admission_no))

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Are you sure the book presetend to you is the one the student borrowed.')

        self.assertTemplateUsed(response, "library/borrowed_confirm_delete.html")

        self.assertEqual(response.resolver_match.func, delete_borrowed_book_record)



















    

