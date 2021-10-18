from getpass import getpass
from io import StringIO
from os import write
import sqlite3
from datetime import date, datetime
import random
import string
import csv, re
import bcrypt

#Admin username: amdin
#Admin pasword: admin123

conn = sqlite3.connect("Mobile.db")
cur = conn.cursor()

#ACCOUNT TABLE
query = "CREATE TABLE IF NOT EXISTS account_table (ID INTEGER PRIMARY KEY AUTOINCREMENT, email VARCHAR(255), username VARCHAR(255), fullname VARCHAR(255), acc_number INTEGER, balance INTEGER DEFAULT '100', password VARCHAR(255), pin INTEGER )"
cur.execute(query)


#CREATING TRANSACTION TABLE
queryx = """ CREATE TABLE IF NOT EXISTS transactions(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255),
    from_acc_num VARCHAR(255) DEFAULT "NULL",
    to_acc_num VARCHAR(255) DEFAULT "NULL",
    amount VARCHAR (255),
    balance VARCHAR(255),
    transaction_type VARCHAR(255),
    time VARCHAR(255),
    UNIQUE (username)
    ) """
cur.execute(queryx)    

def gen_pincode():
    #Generating random pincode
    numbers = string.digits
    pin = []
    for x in range(4):
        pin.append(random.choice(numbers))
    return ("".join(pin))

def gen_acc_number():
    number = string.digits
    acc_number = []
    for x in range (14):
        acc_number.append(random.choice(number))
    return "".join(acc_number)

def customer_menu(username):

    while 1:
        print("\n")
        print("******CUSTOMER MENU*********")
        print("\n")
        print("1. Transfer Funds")
        print("2. Withdraw Funds")
        print("3. Deposit Funds")
        print("4. Check Account Balance")
        print("5. Change PIN")
        print("6. Change Password")
        print("7. Mini Statement")
        print("8. Log Out")
        user_input = input("Select an Option: ")

        query  = "SELECT balance,pin,acc_number,password FROM account_table WHERE username = ?"
        query_value = (username,)
        cur.execute(query, query_value)
        results = cur.fetchall()
        for result in results:
            balance = result[0]
            pin = result [1]
            acc_number = result[2]
            password = result[3]

            #transferring money
            if user_input =="1":
                if balance <= 0:
                    print("Insufficient Funds.")
                else:
                    acc_num = int(input("Enter Account number: "))
                    confirm_acc_num = int(input("Confirm Account Number: "))
                    if acc_num ==confirm_acc_num:
                        amount = float(input("Enter Amount: "))
                        if amount <= balance:
                            pincode = int(input("Enter Pin"))
                            if pincode ==pin:
                                print(f"{amount} Transferred to { acc_num} successfully")
                                balance = balance - amount
                                print(f" Account Balance is {balance}")
                                update_query = "UPDATE account_table SET balance = ? WHERE username = ?"
                                update_query_values = (balance, username)
                                cur.execute(update_query,update_query_values)
                                
                                #populating transaction database table for sending funds
                                transaction_type = "Transfer"
                                time = datetime.today()
                                time = time.strftime("%d-%m-%Y, %H:%M:%S")
                                insert_query = "INSERT INTO transactions (username, from_acc_num, to_acc_num, amount, balance, transaction_type, time) VALUES (?,?,?,?,?,?,?)"
                                insert_query_values = (username,acc_number, acc_num, amount, balance, transaction_type, time)
                                cur.execute(insert_query, insert_query_values)
                                conn.commit()
                            else:
                                print("Invalid Pin")
                        else:
                            print("Amount Insufficient")
                    else:
                        print("Account number does not match")

            elif user_input =="2":
                amount = float(input("Enter amount to Withdraw: "))
                if amount <= balance:
                    pincode = int(input("Enter PIN: "))
                    if pincode ==pin:
                        print(f"{amount} withdrawn successfully")
                        balance = balance - amount
                        query = "UPDATE account_table SET balance =? WHERE username = ?"
                        query_value = (balance, username)
                        cur.execute(query,query_value)

                        #populating transaction database table for withdrawal
                        transaction_type = "Withdrawal"
                        time = datetime.today()
                        time = time.strftime("%d-%m-%Y, %H:%M:%S")
                        insert_query = "INSERT INTO transactions (username, from_acc_num, amount, balance, transaction_type, time) VALUES (?,?,?,?,?,?)"
                        insert_query_values = (username, acc_number, amount, balance, transaction_type, time)
                        cur.execute(insert_query, insert_query_values)
                        
                        conn.commit()
                    else:
                        print("Invalid PIN")
                else:
                    print("Insufficent Amount to Withdraw")

            elif user_input =="3":
                amount = float(input("Enter amount to Deposit: "))
                balance = balance + amount
                acc_num = int(input("Enter Account Number: "))
                if acc_num ==acc_number:
                    pincode = int(input("Enter Pin to Confirm Deposit: "))
                    if pincode ==pin:
                        print(f"{amount} has been deposited to your account {acc_number} successfully. Your balance is {balance}")
                        query = "UPDATE account_table SET balance = ? WHERE username = ?"
                        query_value = (balance, username)
                        cur.execute(query,query_value)
                        
                        #populating transaction database table for depositing funds
                        transaction_type = "Deposit"
                        time = datetime.today()
                        time = time.strftime("%d-%m-%Y, %H:%M:%S")
                        insert_query = "INSERT INTO transactions (username, amount, balance, transaction_type, time) VALUES (?,?,?,?,?)"
                        insert_query_values = (username, amount, balance, transaction_type, time)
                        cur.execute(insert_query, insert_query_values)
                        
                        conn.commit()
                    else:
                        print("Invalid PIN")
                else:
                    print("Account number is not Accurate")

            elif user_input =="4":
                print(f"Account balance is {balance}")

            elif user_input =="5":
                old_pin = int(input("Enter Previous PIN: "))
                if old_pin == pin:
                    new_pin = int(input("Enter new PIN: "))
                    confirm_new_pin = int(input("Confirm PIN: "))
                    if new_pin ==confirm_new_pin:
                        pin = new_pin 
                        query = "UPDATE account_table SET pin =? WHERE username = ?"
                        query_value = (pin, username)
                        cur.execute(query, query_value)
                        conn.commit()
                    else:
                        print("PIN does not match")
                else:
                    print("Invalid PIN")

            elif user_input =="6":
                old_password = (input("Enter Previous Password: "))
                if password == bcrypt.hashpw(str.encode(old_password), password):
                    new_password = (input("Enter New Password: "))
                    while len(new_password) < 8 or len(new_password)> 16:
                        print("Password too Short or too Long (8-16)")
                        new_password = (input("Enter New Password: "))
                    else:
                        confirm_new_password = (input("Confirm Password: "))
                        if new_password ==confirm_new_password:
                            password =  bcrypt.hashpw(str.encode(new_password), bcrypt.gensalt())  #new_password
                            print("Password Set Up Successfully")
                            query = "UPDATE account_table SET password =? WHERE username = ?"
                            query_value = (password, username)
                            cur.execute(query, query_value)
                            conn.commit()
                        else:
                            print("Password does not match")
                else:
                    print("Invalid Password")

            elif user_input =="7":
                query = "SELECT *FROM transactions WHERE username =?"
                query_values = (username,)
                cur.execute(query,query_values)
                results = cur.fetchall()
                if len(results) <=0:
                    print("Sorry. Account contains no transactional History")
                else:    
                    print("Downloading CSV/ EXCEL file")
                    #creating a csv file to contain data
                    with open ("statement.csv", "w") as f:
                        csv_writer = csv.writer(f)
                        csv_writer.writerow(["Transaction ID", "Username", "From Account", "To Account","Amount", "Balance","Transaction Type", "Time"])

                        for result in results:
                            transaction_id = result[0]
                            username = result[1]
                            from_account = result[2]
                            to_account = result[3]
                            amount = result[4]
                            balance = result[5]
                            transaction_type = result[6]
                            time = result[7]
                            
                            csv_writer.writerow([transaction_id, username, from_account,to_account,amount,balance,transaction_type,time])           

            elif user_input =="8":
                quit()
                
            else:
                print("Invalid Option Selected")

def cus_login():
    """Customer Login using email and username. Customer can only login after signing up"""
    print("\n")
    username = input("Enter username: ")
    password = input("Enter password: ")
    query = "SELECT username, password FROM account_table where username =?"
    query_values = (username,)
    cur.execute(query,query_values)
    results = cur.fetchall()
    if len(results) <=0:
        print("Username Not Defined. Create Account to proceed ")
    else:
        for result in results:
            result_username = result[0]
            result_password = result[1]
            
            if username ==result_username:
                if result_password == bcrypt.hashpw(str.encode(password), result_password):
                    customer_menu(username)
                else:
                    print("Incorrect Login")
            else:
                print("Log In Details Not Accurate")



def customer_session(email):
    query = "SELECT acc_number FROM account_table WHERE email =? "
    query_value = (email,)
    cur.execute(query,query_value)
    result = cur.fetchone()
    if result != None :
        print("Email Already Assigned to a Username. Return to Login Or Contact Admin")
    else:   
        username = str(input("Enter username: "))
        cur.execute("SELECT username FROM account_table ")
        records = cur.fetchall()

        record_list = [item for record in records for item in record]
                    
        if username in record_list:
            print(f"{username} already exist. Use another")
        else:
            password = (input("Enter password here: "))
            while len(password) < 8 or len(password) > 16:
                print("Password too short or to long") 
                password = (input("Enter password here: "))
            else:
                password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())

                #query = "CREATE TABLE IF NOT EXISTS account_table (ID INTEGER PRIMARY KEY AUTOINCREMENT, email VARCHAR(255), username VARCHAR(255), fullname VARCHAR(255), acc_number INTEGER, balance INTEGER DEFAULT '100', password VARCHAR(255), pin INTEGER )"
                #cur.execute(query)

                get_query = "SELECT *FROM customers WHERE email = ?"
                get_query_values = (email,)
                cur.execute(get_query, get_query_values)
                results = cur.fetchall()
                for result in results:
                    firstname = result[1]
                    lastname = result[2]
                    acc_number = result[8]
                    pin = result[9]
                    fullname = firstname+ " "+ lastname
                            
                    query_insert = "INSERT INTO account_table (email, username, fullname, acc_number,password, pin) VALUES (?,?, ?,?,?,?)"
                    query_insert_values = (email, username, fullname, acc_number,password, pin)
                    cur.execute(query_insert, query_insert_values)
                    conn.commit()
                    print("Account Created Successfully")
                    user_input = input("Proceed to Log IN (Y / N ): ").upper()
                    while True:
                        if user_input == "Y":
                            customer_menu(username)
                        else:
                            break

def auth_customer():
    #Customer Authorisation. Function enables customer to set up account after admin registration or Login if account has already been set up
    print("\n")
    print("---- CUSTOMER ACCOUNT SIGN UP ----")
    print("\n")
    print("1. Create Account")
    print("2. Already Have Account. LOGIN")
    user_input = input("Select Option: ")
    if user_input =="1":
        print("\n")
        print("Creating Count....")
        print("\n")
        email = input("enter your email address: ")
        pincode = input("enter your pincode: ")
        query = "SELECT *FROM customers WHERE email =? AND pincode=?"
        query_values = (email, pincode)
        cur.execute(query,query_values)
        results = cur.fetchall()
        if len(results) <=0:
            print("Records Not In System. Contact Admin")
        else: 
            customer_session(email)

    elif user_input =="2":
        cus_login()
            

def admin_session():
    #Admin Session. Function contains admin functionalities
    while True:
        print("\n")
        print("*********Admin Menu**********")
        print("\n")
        print("1. Register user ")
        print("2. Delete existing user")
        print("3. Update user Information")
        print("4. Log Out")
        print("\n")

        user_input = input("Enter Option: ")
        if user_input =="1":
            print("Creating User Account....")
            print("\n")
            
            customer_table = """ CREATE TABLE IF NOT EXISTS customers 
            (   customerID INTEGER PRIMARY KEY AUTOINCREMENT,
                firstname VARCHAR(255),
                lastname VARCHAR (255),
                DOB DATE,
                marital_status VARCHAR(255),
                nationality VARCHAR(255),
                phone_number INT,
                email VARCHAR(255),
                acc_number INT,
                pincode INTEGER,
                date_created DATE
                
            ) """
            cur.execute(customer_table)
            
            firstname = input("Enter firstname: ").capitalize()
            lastname = input("Enter lastname: ").capitalize()
            DOB = input("Enter date of birth: DD/MM/YYYY : ")

            #S = SINGLES| M= MARRIED | D = DIVORCED | O = OTHERS
            marital_status = input("Enter marital status ( S / M / D / O):").upper()
            if marital_status == 'S':
                marital_status = "Single"
            elif marital_status == 'M':
                marital_status ="Married"
            elif marital_status == "D":
                marital_status = "Divorced"
            else:
                marital_status = "Others"

            nationality = input("Enter nationality: ").capitalize()

            phone_number = (input("Enter phone number: 233(0)"))
            while len(phone_number) !=9:     
                print("Invalid phone number")
                phone_number = (input("Enter phone number: 233(0)"))
            phone_number = str("233"+ phone_number)
            phone_number = int(phone_number)
            email = input("Enter email address: ")
            while not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                print("Invalid Email")
                email = input("Enter a valid email address: ")

            else:
                acc_number = gen_acc_number()
                pincode = gen_pincode()
                date_created = date.today()
                    
                query = """ INSERT INTO customers (firstname, lastname, DOB, marital_status, nationality, phone_number, email, acc_number, pincode, date_created) VALUES (?,?,?,?,?,?,?,?,?,?) """
                query_values = (firstname, lastname, DOB, marital_status, nationality, phone_number, email, acc_number, pincode, date_created)
                cur.execute(query,query_values)
                conn.commit()
                print("Customer Registered Successfully")
            

        elif user_input == "2":
            firstname = input("Enter firstname: ").capitalize()
            lastname = input("Enter Lastname: ").capitalize()
            
            query = "SELECT * FROM customers WHERE firstname =? AND lastname = ? "
            query_valuex = (firstname, lastname)
            cur.execute(query, query_valuex)
            result = cur.fetchall()
            if len(result) < 1:
                print(f"{firstname} {lastname} does not exist")
            else:
                query = ("DELETE FROM customers WHERE firstname = ? and lastname = ?")
                query_values = (firstname, lastname)
                cur.execute(query,query_values)
                conn.commit()
                print(f"{firstname} {lastname} deleted.")

        elif user_input =="3":
            while 1:
                print("\n")
                print("------ SELECT OPTION TO UPDATE INFO -----")
                print("\n")
                print("1. Change Firstname")
                print("2. Change Lastname")
                print("3. Change Date Of Birth")
                print("4. Change Marital Status")
                print("5. Change Nationality")
                print("6. Change Phone Number")
                print("7. Change Email Address")
                print("8. Back")
                print("\n")
                user_input = input("Select Option: ")
                if user_input =="1":
                    email = input("Enter Email address: ")
                    new_firstname = input("Enter new firstname here: ")
                    query_values = (new_firstname, email)
                    query = "UPDATE customers SET firstname =? WHERE email = ?" 
                    cur.execute(query,query_values)
                    conn.commit()
                elif user_input =="2":
                    email = input("Enter Email address: ")
                    new_lastnamename = input("Enter new lastname here: ")
                    query_values = (new_lastnamename, email)
                    query = "UPDATE customers SET lastname =? WHERE email = ?" 
                    cur.execute(query,query_values)
                    conn.commit()
                elif user_input =="3":
                    email = input("Enter Email address: ")
                    new_DOB = input("Enter new DATE of Birth here: ")
                    query_values = (new_DOB, email)
                    query = "UPDATE customers SET DOB =? WHERE email = ?" 
                    cur.execute(query,query_values)
                    conn.commit()
                elif user_input =="4":
                    email = input("Enter Email address: ")
                    new_marital_status = input("Enter new marital_status here ( S / M / D / O): ").upper()
                    #S = SINGLES| M= MARRIED | D = DIVORCED | O = OTHERS
                    if new_marital_status == 'S':
                        new_marital_status = "Single"
                    elif new_marital_status == 'M':
                        new_marital_status ="Married"
                    elif new_marital_status == "D":
                        new_marital_status = "Divorced"
                    else:
                        new_marital_status = "Others"
                    query_values = (new_marital_status, email)
                    query = "UPDATE customers SET marital_status =? WHERE email = ?" 
                    cur.execute(query,query_values)
                    conn.commit()
                elif user_input =="5":
                    email = input("Enter Email address: ")
                    new_nationality = input("Enter new nationality here: ")
                    query_values = (new_nationality, email)
                    query = "UPDATE customers SET nationality =? WHERE email = ?" 
                    cur.execute(query,query_values)
                    conn.commit()
                elif user_input =="6":
                    email = input("Enter Email address: ")
                    new_phone_number = input("Enter new phone number here: 233(0)")
                    while len(new_phone_number) != 9:     
                        print("Invalid phone number")
                        new_phone_number = (input("Enter phone number: 233(0)"))
                    new_phone_number = str("233"+ new_phone_number)
                    query_values = (int(new_phone_number), email)
                    query = "UPDATE customers SET phone_number =? WHERE email = ?" 
                    cur.execute(query,query_values)
                    conn.commit()
                elif user_input =="7":
                    email = input("Enter Email address: ")
                    new_email = input("Enter new email address here: ")
                    query_values = (new_email, email)
                    query = "UPDATE customers SET email =? WHERE email = ?" 
                    cur.execute(query,query_values)
                    conn.commit()
                elif user_input =="8":
                    break
                else:
                    print("Invalid")                

        elif user_input=="4":
            break;
        else:
            print("Invalid Option Selected")


def auth_admin():
    #Admin authorization - (Login)
    username = str("admin")
    password = str("admin123")
    username_input = str(input("Enter Username: "))
    password_input = getpass("Enter password: ")
    if username_input==username:
        if password_input==password:
            print("Log In Successful")
            admin_session()
        else:
            print("Invalid Password")
    else:
        print("Invalid Log In Details")

#Main menu
def main():
    while 1:
    
        print("\n")
        print("------ WELCOME TO LEINAD BANKING ---------")
        print("\n")
        print("1. Log In as Admin")
        print("2. Customer Sign In")
        print("3. QUIT")
        print("\n")

        user_input = (input("Enter user input: "))
        if user_input == "1":
            auth_admin()
        elif user_input == "2":
            auth_customer()
        elif user_input =="3":
            quit()
        else:
            print("Invalid Option")

main()

