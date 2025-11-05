import mysql.connector

# PYTHON-MYSQL INTEGRATION
mycon = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "mysql69",
    database = "lms"
)
cursor = mycon.cursor()

# ADMIN LOGIN
def admin_login():
    usn = input("Enter username: ").strip()
    pswd = input("Enter password: ").strip()

    query = "select * from admin where username = %s and password = %s"
    cursor.execute(query,(usn,pswd))
    row = cursor.fetchone()
     
    if row:
        return True
    else: 
        return False   

def table_generator(row,header):
    
    col_width = [len(h) for h in header]

    for r in row:
        for i in range(len(r)):
            width = len(str(r[i]))
            if width > col_width[i]:
                col_width[i] = width
    
    line = ""
    for i in range(len(header)):
        line += (header[i]).ljust(col_width[i])
        if i < (len(header) - 1):
            line += " | "
    print(line)

    x = 0
    for i in col_width:
        x += i
    x += 3 * (len(header) - 1)
    print("-" * x)

    for r in row:
        row_line = ""
        for i in range(len(r)):
            row_line += (str(r[i])).ljust(col_width[i])
            if i < (len(r)-1):
                row_line += " | "
        print(row_line)

def get_choice(prompt):
    while True:
        x = input(prompt).strip()
        if x.upper()=="Y":
            return True
        elif x.upper()=="N":
            return False
        else:
            print("\n---[Invalid Choice]---")

def get_retry_choice(retry_label="Re-Enter",back_label="Back"):
    while True:
        print(f"\n1. {retry_label}")
        print(f"2. {back_label}")
        try:
            choice = int(input("\nEnter choice: "))
        except ValueError:
            print("\n---[Invalid Input]---\n")
            continue
        match choice:
            case 1:
                print()
                return True
            case 2: 
                print()
                return False
            case _:
                print("\n---[Invalid Choice]---")
                
def search_books(book_id=None,title=None,author=None,genre=None,isbn=None): 
    query = "select * from book where 1=1"
    args = []
    if book_id is not None:
        query += " and book_id = %s"
        args.append(book_id)
    if title is not None:
        query += " and title = %s"
        args.append(title)
    if author is not None:
        query += " and author = %s"
        args.append(author)
    if genre is not None:
        query += " and genre = %s"
        args.append(genre)
    if isbn is not None:
        query += " and isbn = %s"
        args.append(isbn)
    
    cursor.execute(query, tuple(args))
    return cursor.fetchall()

def get_book(field="book_id"):
    labels = {
        "book_id": ("Book ID", int),
        "title": ("Title", str),
        "author": ("Author", str),
        "genre": ("Genre", str),
        "isbn": ("ISBN Code", str)
    }
    display,cast = labels[field]
    while True:
        try:
            value = cast(input(f"Enter {display}: "))
        except ValueError:
            print("\n---[Invalid Input]---\n")
            continue
        
        key = {field:value}
        result = search_books(**key)

        if result:
            return result
        else:
            print("\n---[Book Not Found]---")
            if get_retry_choice("Re-Enter"):
                continue
            else:
                return None

def is_issued(id):
    query = "select * from rental where book_id = %s and return_date is null"
    cursor.execute(query,(id,))
    x = cursor.fetchall()

    if x:
        table_generator(x,["RENTAL ID","USER ID","BOOK ID","ISSUE DATE","DUE DATE","RETURN DATE","FINE"])
        print()
        return True
    else:
        return False

def add_book():
    while True:
        print("\n Add Book")
        print("==========")
        title = input("Enter Title of the book: ").strip()
        author = input("Enter name of Author: ").strip()
        genre = input("Enter the Genre: ").strip()
        isbn = input("Enter ISBN Code: ").strip()
        total_copies = int(input("Enter number of total copies: "))
        available_copies = total_copies

        print()
        l=[(title,author,genre,isbn,total_copies)]
        table_generator(l,["TITLE","AUTHOR","GENRE","ISBN","TOTAL COPIES"])

        
        if get_choice("\nCommit this entry? (y/n): "):
            query = "insert into book (title,author, genre,isbn,total_copies,available_copies) values (%s,%s,%s,%s,%s,%s)"
            values = (title,author,genre,isbn,total_copies,available_copies)
            cursor.execute(query,values)
            mycon.commit()
            print("\n\n===[Book Added Successfully]===\n")
            return
        else:
            if get_retry_choice("Re_Enter Details"):
                continue
            else:
                return

def update_book():
    def field_updater(id,field,display_name,current,cast=str):
        while True:
            new = cast(input(f"Enter new {display_name}: "))
            if get_choice(f'Change {display_name} from "{current}" to "{new}"? (y/n): '):
                query = f"update book set {field} = %s where book_id = %s"
                cursor.execute(query,(new,id))
                mycon.commit()
                print(f"\n\n===[Book Updated Successfully]===\n")
                return
            else:
                if get_retry_choice(f"Re-Enter {display_name}"):
                    continue
                else:
                    return

    while True: 
        print("\n Update Book")
        print("=============")
        l = get_book()
        if l is None:
            return
        print()
        table_generator(l,["BOOK ID","TITLE","AUTHOR","GENRE","ISBN","TOTAL COPIES","AVAILABLE COPIES"])

        if get_choice("\nSelect this book for updation? (y/n): "):
            break
        else:
            if get_retry_choice("Re-Enter ID"):
                continue
            else:
                return
    while True:
        row = l[0]
        print("\n---Choose field to update---")
        print("1. Title")
        print("2. Author")
        print("3. Genre")
        print("4. ISBN Code")
        print("5. Total Copies")
        print("6. Available Copies")
        print("7. Back")

        choice = int(input("\nEnter choice: "))

        match choice:
            case 1:
                field_updater(row[0],"title","Title",row[1])
            case 2:
                field_updater(row[0], "author", "Author", row[2])
            case 3:
                field_updater(row[0], "genre", "Genre", row[3])
            case 4:
                field_updater(row[0], "isbn", "ISBN Code", row[4])
            case 5:
                field_updater(row[0], "total_copies", "Total Copies", row[5], int)
            case 6:
                field_updater(row[0], "available_copies", "Available Copies", row[6], int)
            case 7:
                return
            case _:
                print("\n---[Invalid Choice]---")

def view_book():
    def view_by(field=None):
        if field is None:
            rows = search_books()
        else:
            rows = get_book(field)

        if rows:
            print("\n\n")
            table_generator(rows, ["BOOK ID","TITLE","AUTHOR","GENRE","ISBN","TOTAL COPIES","AVAILABLE COPIES"])
            print("\n\n")
    while True:
        print("\n View Book")
        print("===========")
        print("1. By Book ID")
        print("2. By Title")
        print("3. By Author")
        print("4. By Genre")
        print("5. By ISBN Code") 
        print("6. All Records")
        print("7. Back")
        try:
            choice = int(input("\nEnter choice: "))
        except ValueError:
            print("\n---[Invalid Input]---\n")
            continue

        match choice:
            case 1:
                print("\n---By Book ID---")
                view_by("book_id")
            case 2:
                print("\n---By Title---")
                view_by("title")
            case 3:
                print("\n---By Author---")
                view_by("author")
            case 4:
                print("\n---By Genre---")
                view_by("genre")
            case 5:
                print("\n---By ISBN Code---")
                view_by("isbn")
            case 6:
                view_by()
            case 7:
                return
            case _:
                print("\n---[Invalid Choice]---")

def del_book():
    while True: 
        print("\n Delete Book")
        print("=============")
        l = get_book()
        if l is None:
            return
        print()
        if is_issued(l[0][0]):
            print("---[Can't delete. Book is currently issued]---")
            return
        else:
            table_generator(l,["BOOK ID","TITLE","AUTHOR","GENRE","ISBN","TOTAL COPIES","AVAILABLE COPIES"])
            if get_choice("\nSelect this book for deletion? (y/n): "):
                query = "delete from book where book_id = %s"
                cursor.execute(query,(l[0][0],))
                mycon.commit()
                print("\n\n===[Book Deleted Successfully]===\n")
                
                break
            else:
                if get_retry_choice("Re-Enter ID"):
                    continue
                else:
                    return



print("\n LIBRARY MANAGEMENT SYSTEM")
print("===========================\n")

# MAIN MENU
while True:
    print(" Main Menu")
    print("===========")
    print("1. Admin Login")
    print("2. User Login")
    print("3. EXIT")
    try:
        choice = int(input("\nEnter choice: "))
    except ValueError:
        print("\n---[Invalid Input]---\n")
        continue

    match choice:
        case 1:
            # ADMIN LOGIN
            print("\n Admin Login")
            print("=============")
            for i in range(3):
                if admin_login():
                    print("\n---[Login Successful]---\n")
                    break
                else:
                    print(f"\n---[Invalid Credentials: Attempt {i+1}/3]---\n")
            else:
                print("~LOGIN FAILED~\n")
                continue

            #ADMIN MENU   
            while True:
                print(" Admin Menu")
                print("============")
                print("1. Manage Books")
                print("2. Manage Users")
                print("3. Manage Employees")
                print("4. View Rentals")
                print("5. Calculate Fine")
                print("6. Back")
                try:
                    choice = int(input("\nEnter choice: "))
                except ValueError:
                    print("\n---[Invalid Input]---\n")
                    continue
                
                match choice:
                    case 1:
                        # MANAGE BOOKS
                        while True:
                            print("\n Manage Books")
                            print("==============")
                            print("1. Add Book")
                            print("2. Update Book")
                            print("3. View Book")
                            print("4. Delete Book")
                            print("5. Back")
                            try:
                                choice = int(input("\nEnter choice: "))
                            except ValueError:
                                print("\n---[Invalid Input]---\n")
                                continue

                            match choice:
                                case 1:
                                    add_book()
                                    continue
                                case 2:
                                    update_book()
                                    continue
                                case 3:
                                    view_book()
                                    continue
                                case 4:
                                    del_book()
                                    continue
                                case 5:
                                    break
                                case _:
                                    print("\n---[Invalid Choice]---")
                    # case 2:
                    #     # MANAGE USERS
        case 2:
            break
        case 3:
            if get_choice("\nAre you sure you want to EXIT? (y/n): "):
                print("\n~{Thank You}~\n")
                mycon.close()
                break
            else:
                print("\n~{Going Back To Main Menu}~\n")
                continue
        case _:
            print("\n---[Invalid Choice]---")
            