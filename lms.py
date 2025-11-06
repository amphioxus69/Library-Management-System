import mysql.connector
from datetime import datetime

# ==========[DATABASE CONNECTION]==========
mycon = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "mysql69",
    database = "lms"
)
cursor = mycon.cursor()

# ----------[ADMIN LOGIN]----------
def admin_login():
    usn = input("Enter username: ").strip()
    pswd = input("Enter password: ").strip()

    query = "select * from admins where username = %s and password = %s"
    cursor.execute(query,(usn,pswd))
    row = cursor.fetchone()
     
    if row:
        return True
    else: 
        return False   

# ----------[TABLE HEADERS]----------
table_headers = {
    "books":["BOOK ID","TITLE","AUTHOR","GENRE","ISBN","TOTAL COPIES","AVAILABLE COPIES"],
    "users": ["USER ID","NAME","EMAIL","PASSWORD","CONTACT","DATE JOINED"],
    "rentals": ["RENTAL ID","USER ID","BOOK ID","ISSUE DATE","DUE DATE","RETURN DATE"],
    "employees": ["EMPLOYEE ID","NAME","EMAIL","CONTACT","DESIGNATION","SALARY","DATE JOINED"]
}

# ==========[INPUT HELPERS]==========
def get_choice(prompt):
    while True:
        x = input(prompt).strip()
        if x.upper()=="Y":
            return True
        elif x.upper()=="N":
            return False
        else:
            print("\n---[Invalid Choice]---")
            print()
def get_retry_choice():
    while True:
        print(f"\n1. Re-Enter")
        print(f"2. Back")
        try:
            choice = int(input("\nEnter choice: "))
        except ValueError:
            print("\n---[Invalid Input]---\n")
            continue
        match choice:
            case 1:
                return True
            case 2: 
                return False
            case _:
                print("\n---[Invalid Choice]---")

# ==========[UNIVERSAL FUNCTIONS]==========

# ----------TABLE GENERATOR----------
def table_generator(rows,header):
    
    if not rows:
        print("\n---[No Records Found]---")

    col_width = [len(h) for h in header]

    for r in rows:
        for i in range(len(r)):
            width = len(str(r[i]))
            if width > col_width[i]:
                col_width[i] = width
    
    header_line = ""
    for i in range(len(header)):
        header_line += (header[i]).ljust(col_width[i])
        if i < (len(header) - 1):
            header_line += " | "
    print("\n"+header_line)

    total_width = 0
    for i in col_width:
        total_width += i
    total_width += 3 * (len(header) - 1)
    print("-" * total_width)

    for r in rows:
        row_line = ""
        for i in range(len(r)):
            row_line += (str(r[i])).ljust(col_width[i])
            if i < (len(r)-1):
                row_line += " | "
        print(row_line)
    print()

# ----------UNIVERSAL SEARCH----------
def search(table,**conditions):
    
    keys = conditions.keys()
    values = conditions.values()

    query = f"select * from {table} where 1=1"
    for k in keys:
        query += f" and {k} = %s"
    
    cursor.execute(query,tuple(values))
    return cursor.fetchall()
        
# ----------UNIVERSAL ADD----------
def add(table,**data):

    columns = data.keys()
    values = data.values()

    col_str = ", ".join(columns)
    l = ["%s"]*len(values)
    placeholders = ", ".join(l)

    query = f"insert into {table} ({col_str}) values ({placeholders})"
    cursor.execute(query,tuple(values))
    mycon.commit()

    print("\n\n===[Record Added Successfully]===\n")

# ----------UNIVERSAL UPDATE----------
def update(table,key_field,key_value,field,current,cast=str):
    while True:
        try:
            new_value = cast(input(f"\nEnter new {field.replace('_',' ').title()}: "))
        except ValueError:
            print("\n---[Invalid Input]---\n")
            continue

        if get_choice(
            f'Change {field.replace("_"," ").title()} from "{current}" to "{new_value}"? (y/n): '
        ):
            query = f"UPDATE {table} SET {field} = %s WHERE {key_field} = %s"
            cursor.execute(query, (new_value, key_value))
            mycon.commit()
            print("\n\n===[Record Updated Successfully]===\n")
            return
        else:
            if get_retry_choice():
                continue
            else:
                return

# ----------UNIVERSAL DELETE----------
def delete(table,key_field,key_value):
    query = f"delete from {table} where {key_field} = %s"
    cursor.execute(query,(key_value,))
    mycon.commit()

    print("\n\n===[Record Deleted Successfully]===\n")

# ----------UNIVERSAL VIEW----------
def view(table,field,value):
    query = f"select * from {table} where {field} = %s"
    cursor.execute(query,(value,))
    rows = cursor.fetchall()

    if rows:
        print()
        table_generator(rows,table_headers[table])
        print()
    else:
        print("\n---[No Records Found]---\n")

# ----------GET RECORD BY FIELD----------
def get_record(table,field,cast=str):
    while True:
        try:
            value = cast(input(f"Enter {field.replace('_',' ').title()}: ").strip())
        except ValueError:
            print("\n---[Invalid Input]---\n")
            continue

        rows = search(table, **{field: value})

        if rows:
            return rows
        else:
            print(f"\n---[Record Not Found]---")
            if get_retry_choice():
                continue
            else:
                return None

# ----------[MANAGE BOOKS]----------
def manage_books():
    
    def add_book():
        while True:
            print("\n Add Book")
            print("==========")
            title = input("Enter Title: ").strip()
            author = input("Enter Author: ").strip()
            genre = input("Enter Genre: ").strip()
            isbn = input("Enter ISBN Code: ").strip()
            try:
                total_copies = int(input("Enter Total Copies: "))
            except ValueError:
                print("\n---[Invalid Input]---")
                continue
            available_copies = total_copies

            row=[(title,author,genre,isbn,total_copies,available_copies)]
            col = (table_headers["books"])[1:]
            table_generator(row,col)
            
            if get_choice("Commit this entry? (y/n): "):
                add(
                    "books",
                    title=title,
                    author=author,
                    genre=genre,
                    isbn=isbn,
                    total_copies=total_copies,
                    available_copies=available_copies
                )
                return
            else:
                if get_retry_choice():
                    continue
                else:
                    return
    def update_book():
        while True: 
            print("\n Update Book")
            print("=============")
            rows = get_record("books","book_id",cast=int)
            if rows is None:
                return
            print()
            table_generator(rows,table_headers["books"])

            if get_choice("\nSelect this book for updation? (y/n): "):
                break
            else:
                if get_retry_choice():
                    continue
                else:
                    return
        while True:
            row = rows[0]
            print("\n---Choose field to update---\n")
            print("1. Title")
            print("2. Author")
            print("3. Genre")
            print("4. ISBN Code")
            print("5. Total Copies")
            print("6. Available Copies")
            print("7. Back")

            try:
                choice = int(input("\nEnter choice: "))
            except ValueError:
                print("\n---[Invalid Input]---\n")
                continue

            match choice:
                case 1:update("books","book_id",row[0],"title",row[1])
                case 2:update("books","book_id",row[0],"author",row[2])
                case 3:update("books","book_id",row[0],"genre",row[3])
                case 4:update("books","book_id",row[0],"isbn",row[4])
                case 5:update("books","book_id",row[0],"total_copies",row[5],int)
                case 6:update("books","book_id",row[0],"available_copies",row[6],int)
                case 7:return
                case _:print("\n---[Invalid Choice]---")
    def view_book():
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
                print("\n---[Invalid Input]---")
                continue

            match choice:
                case 1:
                    print("\n---By Book ID---")
                    rows = get_record("books", "book_id", int)
                case 2:
                    print("\n---By Title---")
                    rows = get_record("books", "title")
                case 3:
                    print("\n---By Author---")
                    rows = get_record("books", "author")
                case 4:
                    print("\n---By Genre---")
                    rows = get_record("books", "genre")
                case 5:
                    print("\n---By ISBN Code---")
                    rows = get_record("books", "isbn")
                case 6:
                    rows = search("books")
                case 7:
                    return
                case _:
                    print("\n---[Invalid Choice]---")
                    continue

            if rows:
                print()
                table_generator(rows, table_headers["books"])
                print()
    def del_book():
        while True: 
            print("\n Delete Book")
            print("=============")
            rows = get_record("books","book_id",cast=int)
            if rows is None:
                return
            print()
            table_generator(rows,table_headers["books"])

            if get_choice("\nSelect this book for deletion? (y/n): "):
                delete("books","book_id",rows[0][0])
                break
            else:
                if get_retry_choice():
                    continue
                else:
                    return 

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
            case 1:add_book()
            case 2:update_book()
            case 3:view_book()
            case 4:del_book()
            case 5:break
            case _: print("\n---[Invalid Choice]---")

# ----------[MANAGE USERS]----------
def manage_users():

    def add_user():
        while True:
            print("\n Add User")
            print("==========")
            name = input("Enter Name: ").strip()
            email = input("Enter Email: ").strip()
            pswd = input("Enter Password: ").strip()
            contact = input("Enter Contact: ").strip()
            date_str = input("Enter Date Joined (YYYY-MM-DD): ").strip()
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print("\n---[Invalid Input]---")
                continue

            row=[(name,email,pswd,contact,date)]
            col = (table_headers["users"])[1:]
            table_generator(row,col)
            
            if get_choice("Commit this entry? (y/n): "):
                add(
                    "users",
                    name=name,
                    email=email,
                    password=pswd,
                    contact=contact,
                    date_joined=date
                )
                return
            else:
                if get_retry_choice():
                    continue
                else:
                    return
    def update_user():
        while True: 
            print("\n Update Book")
            print("=============")
            rows = get_record("users","user_id",cast=int)
            if rows is None:
                return
            print()
            table_generator(rows,table_headers["users"])

            if get_choice("\nSelect this user for updation? (y/n): "):
                break
            else:
                if get_retry_choice():
                    continue
                else:
                    return
        while True:
            row = rows[0]
            print("\n---Choose field to update---\n")
            print("1. Name")
            print("2. Email")
            print("3. Password")
            print("4. Contact")
            print("5. Date joined")
            print("6. Back")

            try:
                choice = int(input("\nEnter choice: "))
            except ValueError:
                print("\n---[Invalid Input]---\n")
                continue

            match choice:
                case 1:update("users","user_id",row[0],"name",row[1])
                case 2:update("users","user_id",row[0],"email",row[2])
                case 3:update("users","user_id",row[0],"password",row[3])
                case 4:update("users","user_id",row[0],"contact",row[4])
                case 5:update("users","user_id",row[0],"date_joined",row[5])
                case 6:return
                case _:print("\n---[Invalid Choice]---")
    def view_user():
        while True:
            print("\n View User")
            print("===========")
            print("1. By User ID")
            print("2. By Name")
            print("3. By Email")
            print("4. By Password")
            print("5. By Contact") 
            print("6. By Date Joined")
            print("7. All Records")
            print("8. Back")

            try:
                choice = int(input("\nEnter choice: "))
            except ValueError:
                print("\n---[Invalid Input]---")
                continue

            match choice:
                case 1:
                    print("\n---By User ID---")
                    rows = get_record("users", "user_id", int)
                case 2:
                    print("\n---By Name---")
                    rows = get_record("users", "name")
                case 3:
                    print("\n---By Email---")
                    rows = get_record("users", "email")
                case 4:
                    print("\n---By Password---")
                    rows = get_record("users", "password")
                case 5:
                    print("\n---By Contact---")
                    rows = get_record("users", "contact")
                case 6:
                    print("\n---By Date Joined---")
                    rows = get_record("users", "date_joined")
                case 7:
                    rows = search("users")
                case 8:
                    return
                case _:
                    print("\n---[Invalid Choice]---")
                    continue

            if rows:
                print()
                table_generator(rows, table_headers["users"])
                print()
    def del_user():
        while True: 
            print("\n Delete User")
            print("=============")
            rows = get_record("users","user_id",cast=int)
            if rows is None:
                return
            print()
            table_generator(rows,table_headers["users"])

            if get_choice("\nSelect this user for deletion? (y/n): "):
                delete("users","user_id",rows[0][0])
                break
            else:
                if get_retry_choice():
                    continue
                else:
                    return


    while True:
        print("\n Manage Users")
        print("==============")
        print("1. Add User")
        print("2. Update User")
        print("3. View User")
        print("4. Delete User")
        print("5. Back")
        try:
            choice = int(input("\nEnter choice: "))
        except ValueError:
            print("\n---[Invalid Input]---\n")
            continue

        match choice:
            case 1:add_user()
            case 2:update_user()
            case 3:view_user()
            case 4:del_user()
            case 5:break
            case _: print("\n---[Invalid Choice]---")

# ----------[MANAGE EMPLOYEES]----------
def manage_employees():

    def add_employee():
        while True:
            print("\n Add employee")
            print("==========")
            name = input("Enter Name: ").strip()
            email = input("Enter Email: ").strip()
            contact = input("Enter Contact: ").strip()
            desig = input("Enter Designation: ").strip()
            salary = input("Enter Salary: ").strip()
            date_str = input("Enter Date Joined (YYYY-MM-DD): ").strip()
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print("\n---[Invalid Input]---")
                continue

            row=[(name,email,contact,desig,salary,date)]
            col = (table_headers["employees"])[1:]
            table_generator(row,col)
            
            if get_choice("Commit this entry? (y/n): "):
                add(
                    "users",
                    name=name,
                    email=email,
                    contact=contact,
                    designation=desig,
                    salary=salary,
                    date_joined=date
                )
                return
            else:
                if get_retry_choice():
                    continue
                else:
                    return
    def update_employee():
        while True: 
            print("\n Update employee")
            print("=============")
            rows = get_record("employees","emp_id",cast=int)
            if rows is None:
                return
            print()
            table_generator(rows,table_headers["employees"])

            if get_choice("\nSelect this employee for updation? (y/n): "):
                break
            else:
                if get_retry_choice():
                    continue
                else:
                    return
        while True:
            row = rows[0]
            print("\n---Choose field to update---\n")
            print("1. Name")
            print("2. Email")
            print("3. Contact")
            print("4. Designation")
            print("5. Salary")
            print("6. Date joined")
            print("7. Back")

            try:
                choice = int(input("\nEnter choice: "))
            except ValueError:
                print("\n---[Invalid Input]---\n")
                continue

            match choice:
                case 1:update("employees","emp_id",row[0],"name",row[1])
                case 2:update("employees","emp_id",row[0],"email",row[2])
                case 3:update("employees","emp_id",row[0],"contact",row[3])
                case 4:update("employees","emp_id",row[0],"designation",row[4])
                case 5:update("employees","emp_id",row[0],"salary",row[5],int)
                case 6:return
                case _:print("\n---[Invalid Choice]---")
    def view_user():
        while True:
            print("\n View User")
            print("===========")
            print("1. By User ID")
            print("2. By Name")
            print("3. By Email")
            print("4. By Password")
            print("5. By Contact") 
            print("6. By Date Joined")
            print("7. All Records")
            print("8. Back")

            try:
                choice = int(input("\nEnter choice: "))
            except ValueError:
                print("\n---[Invalid Input]---")
                continue

            match choice:
                case 1:
                    print("\n---By User ID---")
                    rows = get_record("users", "user_id", int)
                case 2:
                    print("\n---By Name---")
                    rows = get_record("users", "name")
                case 3:
                    print("\n---By Email---")
                    rows = get_record("users", "email")
                case 4:
                    print("\n---By Password---")
                    rows = get_record("users", "password")
                case 5:
                    print("\n---By Contact---")
                    rows = get_record("users", "contact")
                case 6:
                    print("\n---By Date Joined---")
                    rows = get_record("users", "date_joined")
                case 7:
                    rows = search("users")
                case 8:
                    return
                case _:
                    print("\n---[Invalid Choice]---")
                    continue

            if rows:
                print()
                table_generator(rows, table_headers["users"])
                print()
    def del_user():
        while True: 
            print("\n Delete User")
            print("=============")
            rows = get_record("users","user_id",cast=int)
            if rows is None:
                return
            print()
            table_generator(rows,table_headers["users"])

            if get_choice("\nSelect this user for deletion? (y/n): "):
                delete("users","user_id",rows[0][0])
                break
            else:
                if get_retry_choice():
                    continue
                else:
                    return


    while True:
        print("\n Manage Users")
        print("==============")
        print("1. Add User")
        print("2. Update User")
        print("3. View User")
        print("4. Delete User")
        print("5. Back")
        try:
            choice = int(input("\nEnter choice: "))
        except ValueError:
            print("\n---[Invalid Input]---\n")
            continue

        match choice:
            case 1:add_user()
            case 2:update_user()
            case 3:view_user()
            case 4:del_user()
            case 5:break
            case _: print("\n---[Invalid Choice]---")




#__main__
print("\n LIBRARY MANAGEMENT SYSTEM")
print("===========================\n")

# ==========[MAIN MENU]==========
def main():
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
                # print("\n Admin Login")
                # print("=============")
                # for i in range(3):
                #     if admin_login():
                #         print("\n---[Login Successful]---")
                #         break
                #     else:
                #         print(f"\n---[Invalid Credentials: Attempt {i+1}/3]---\n")
                # else:
                #     print("~LOGIN FAILED~\n")
                #     continue

                #ADMIN MENU   
                while True:
                    print("\n Admin Menu")
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
                        case 1: manage_books()
                        case 2: manage_users()
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
            case _:print("\n---[Invalid Choice]---")

if __name__ == "__main__":
    main()