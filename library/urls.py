from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from .views import (home, class_teacher, StudentDeleteView, update_student_name, register_class, category_rows,
                    row_columns, checkbox_options, book_details, bulk_borrowing_view, bulk_borrow_search_form_data,
                    find_matching_records, save_bulk_data, search_student, search_output, 
                    give_out_the_book, search_staff_member, search_findings, give_staff_member_the_book, list_of_borrowed_books,
                    BorrowedBooksListView, print_books_borrowed, student_and_staff_reg_no, unreturned_borrowed_books_details,
                    delete_borrowed_book_record, search_book_info_page, search_book_info, book_info)


urlpatterns = [
    path('', home, name="home"),
    path('class-teacher/', class_teacher, name="class-teacher"),
    path('register-class/', register_class, name="register-class"),
    path('<pk>/remove-student/', StudentDeleteView.as_view(), name="remove-student"),
    path('<student_ID>/update-student-name/', update_student_name, name="update-student-name"),
    path('<category_ID>/category/', category_rows, name="category"),
    path('<row_ID>/row-columns-books/', row_columns, name="row-columns-books"),
    path('checkbox-option/', checkbox_options, name="checkbox-option"),
    path('<book_ID>/book-details/', book_details, name="book-details"),
    path('<column_ID>/bulk-borrowing/', bulk_borrowing_view, name="bulk-borrowing"),
    path('<column_ID>/bulk-borrow-search-form-data/', bulk_borrow_search_form_data, name="bulk-borrow-search-form-data"),
    path('<text>/<column_ID>/find-matching-records/', find_matching_records, name="find-matching-records"),
    path('<column_ID>/<reg_no>/save-bulk/', save_bulk_data, name="save-bulk"),
    path('<book_ID>/search-student/', search_student, name="search-student"),
    path('<student_ID>/<book_ID>/search-output/', search_output, name="search-output"),
    path('<student_ID>/<book_ID>/give-out-the-book/', give_out_the_book, name="give-out-the-book"),
    path('<book_ID>/search-staff-member/', search_staff_member, name="search-staff-member"),
    path('<staff_member_ID>/<book_ID>/search-finding/', search_findings, name="search-finding"),
    path('<staff_member_ID>/<book_ID>/give-staff-member-the-book/', give_staff_member_the_book, name="give-staff-member-the-book"),
    path('borrowed-books/', list_of_borrowed_books, name="borrowed-books"),
    # path('borrowed-books/', BorrowedBooksListView.as_view(), name="borrowed-books"),
    path('print-books-borrowed/', print_books_borrowed, name="print-books-borrowed"),
    path('student-and-staff-reg-no/', student_and_staff_reg_no, name="student-and-staff-reg-no"),
    path('<reg_no>/unreturned-borrowed-books/', unreturned_borrowed_books_details,
          name="unreturned-borrowed-books"),
    path('<book_record_ID>/<object_ID>/<reg_no>/delete-borrowed-book-record/', delete_borrowed_book_record, name="delete-borrowed-book-record"),
    path('search-book-info-page/', search_book_info_page, name="search-book-info-page"),
    path('search-book-info/', search_book_info, name="search-book-info"),
    path('<book_ID>/book-info/', book_info, name="book-info")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)