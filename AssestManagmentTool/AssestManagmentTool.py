import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, Toplevel, filedialog, simpledialog
import csv

def connect_to_database():
    return sqlite3.connect('assets.db')

def create_tables():
    connection = connect_to_database()
    with connection:
        connection.execute('''
            CREATE TABLE IF NOT EXISTS Assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                value DECIMAL(10, 2) NOT NULL,
                responsible_person TEXT,
                purchase_place TEXT,
                city TEXT NOT NULL,
                street TEXT NOT NULL,
                building_number TEXT NOT NULL,
                room TEXT NOT NULL,
                date_received TEXT NOT NULL
            )
        ''')
        connection.execute('''
            CREATE TABLE IF NOT EXISTS Employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                hire_date TEXT NOT NULL,
                department TEXT,
                supervisor TEXT,
                salary DECIMAL(10, 2) NOT NULL
            )
        ''')
        cursor = connection.cursor()
        cursor.execute("PRAGMA table_info(Assets)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'date_received' not in columns:
            connection.execute("ALTER TABLE Assets ADD COLUMN date_received TEXT NOT NULL DEFAULT '01-01-2000'")
        
        cursor.execute("PRAGMA table_info(Employees)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'department' not in columns:
            connection.execute("ALTER TABLE Employees ADD COLUMN department TEXT")
        if 'supervisor' not in columns:
            connection.execute("ALTER TABLE Employees ADD COLUMN supervisor TEXT")
        if 'salary' not in columns:
            connection.execute("ALTER TABLE Employees ADD COLUMN salary DECIMAL(10, 2) NOT NULL DEFAULT 0.0")
    connection.close()

def add_asset(name, description, value, responsible_person, purchase_place, city, street, building_number, room, date_received):
    connection = connect_to_database()
    with connection:
        connection.execute('''
            INSERT INTO Assets (
                name, description, value, responsible_person, purchase_place, city, street, building_number, room, date_received
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, value, responsible_person, purchase_place, city, street, building_number, room, date_received))
    connection.close()

def update_asset(asset_id, name, description, value, responsible_person, purchase_place, city, street, building_number, room, date_received):
    connection = connect_to_database()
    with connection:
        connection.execute('''
            UPDATE Assets SET
                name = ?, description = ?, value = ?, responsible_person = ?, purchase_place = ?, city = ?, street = ?, building_number = ?, room = ?, date_received = ?
            WHERE id = ?
        ''', (name, description, value, responsible_person, purchase_place, city, street, building_number, room, date_received, asset_id))
    connection.close()

def delete_asset(asset_id):
    connection = connect_to_database()
    with connection:
        connection.execute("DELETE FROM Assets WHERE id = ?", (asset_id,))
    connection.close()

def add_employee(name, position, hire_date, department, supervisor, salary):
    connection = connect_to_database()
    with connection:
        connection.execute('''
            INSERT INTO Employees (name, position, hire_date, department, supervisor, salary) VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, position, hire_date, department, supervisor, salary))
    connection.close()

def update_employee(employee_id, name, position, hire_date, department, supervisor, salary):
    connection = connect_to_database()
    with connection:
        connection.execute('''
            UPDATE Employees SET
                name = ?, position = ?, hire_date = ?, department = ?, supervisor = ?, salary = ?
            WHERE id = ?
        ''', (name, position, hire_date, department, supervisor, salary, employee_id))
    connection.close()

def delete_employee(employee_id):
    connection = connect_to_database()
    with connection:
        connection.execute("DELETE FROM Employees WHERE id = ?", (employee_id,))
    connection.close()

def display_assets(sort_by=None, sort_order='ASC', filters=None, value_range=None, date_range=None):
    connection = connect_to_database()
    with connection:
        cursor = connection.cursor()
        query = "SELECT * FROM Assets"
        clauses = []
        if filters:
            filter_clauses = [f"{column} LIKE '%{value}%'" for column, value in filters.items() if value]
            clauses.extend(filter_clauses)
        if value_range:
            min_value, max_value = value_range
            clauses.append(f"value BETWEEN {min_value} AND {max_value}")
        if date_range:
            start_date, end_date = date_range
            clauses.append(f"date_received BETWEEN '{start_date}' AND '{end_date}'")
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        if sort_by:
            query += f" ORDER BY {sort_by} {sort_order}"
        cursor.execute(query)
        assets = cursor.fetchall()
    connection.close()
    return assets

def display_employees():
    connection = connect_to_database()
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Employees")
        employees = cursor.fetchall()
    connection.close()
    return employees

def add_asset_command():
    name = name_entry.get()
    description = description_entry.get()
    value = value_entry.get()
    responsible_person = responsible_person_combobox.get()
    purchase_place = purchase_place_entry.get()
    city = city_entry.get()
    street = street_entry.get()
    building_number = building_number_entry.get()
    room = room_entry.get()

    day = day_var.get()
    month = month_var.get()
    year = year_var.get()
    date_received = f"{day}-{month}-{year}"

    if not (name and value and city and street and building_number and room and day and month and year):
        messagebox.showerror("Error", "Fields marked with * are mandatory!")
        return

    add_asset(name, description, value, responsible_person, purchase_place, city, street, building_number, room, date_received)
    messagebox.showinfo("Success", "Asset added successfully")

def add_employee_command():
    name = employee_name_entry.get()
    position = employee_position_entry.get()
    department = employee_department_entry.get()
    supervisor = employee_supervisor_entry.get()
    salary = employee_salary_entry.get()

    day = emp_day_var.get()
    month = emp_month_var.get()
    year = emp_year_var.get()
    hire_date = f"{day}-{month}-{year}"

    if not (name and position and department and salary and day and month and year):
        messagebox.showerror("Error", "Fields marked with * are mandatory!")
        return

    add_employee(name, position, hire_date, department, supervisor, salary)
    messagebox.showinfo("Success", "Employee added successfully")

def show_assets(assets, title="Assets"):
    if not assets:
        messagebox.showinfo(title, "No assets found")
        return
    top = Toplevel(root)
    top.title(title)
    tree = ttk.Treeview(top)
    tree["columns"] = ("ID", "Name", "Description", "Value", "Responsible Person", "Purchase Place", "City", "Street", "Building Number", "Room", "Date Received")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    for asset in assets:
        tree.insert("", "end", values=asset)
    tree.pack(fill=tk.BOTH, expand=1)
    scrollbar = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

def show_employees(employees, title="Employees"):
    if not employees:
        messagebox.showinfo(title, "No employees found")
        return
    top = Toplevel(root)
    top.title(title)
    tree = ttk.Treeview(top)
    tree["columns"] = ("ID", "Name", "Position", "Hire Date", "Department", "Supervisor", "Salary")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    for employee in employees:
        tree.insert("", "end", values=employee)
    tree.pack(fill=tk.BOTH, expand=1)
    scrollbar = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

def display_assets_command():
    sort_by = sort_by_combobox.get()
    sort_order = sort_order_combobox.get()
    filters = {
        "name": name_filter_entry.get(),
        "description": description_filter_entry.get(),
        "value": value_filter_entry.get(),
        "responsible_person": responsible_person_filter_entry.get(),
        "purchase_place": purchase_place_filter_entry.get(),
        "city": city_filter_entry.get(),
        "street": street_filter_entry.get(),
        "building_number": building_number_filter_entry.get(),
        "room": room_filter_entry.get()
    }
    min_value = min_value_entry.get()
    max_value = max_value_entry.get()
    value_range = (min_value, max_value) if min_value and max_value else None

    start_day = start_day_var.get()
    start_month = start_month_var.get()
    start_year = start_year_var.get()
    end_day = end_day_var.get()
    end_month = end_month_var.get()
    end_year = end_year_var.get()

    start_date = f"{start_day}-{start_month}-{start_year}" if start_day and start_month and start_year else None
    end_date = f"{end_day}-{end_month}-{end_year}" if end_day and end_month and end_year else None

    date_range = (start_date, end_date) if start_date and end_date else None

    assets = display_assets(sort_by, sort_order, filters, value_range, date_range)
    show_assets(assets, title="Display Asset List")

def display_employees_command():
    employees = display_employees()
    show_employees(employees, title="Display Employee List")

def edit_asset_command(asset):
    asset_id = asset[0]

    edit_window = Toplevel(root)
    edit_window.title("Edit Asset")

    tk.Label(edit_window, text="Name:").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(edit_window)
    name_entry.grid(row=0, column=1, padx=5, pady=5)
    name_entry.insert(0, asset[1])

    tk.Label(edit_window, text="Description:").grid(row=1, column=0, padx=5, pady=5)
    description_entry = tk.Entry(edit_window)
    description_entry.grid(row=1, column=1, padx=5, pady=5)
    description_entry.insert(0, asset[2])

    tk.Label(edit_window, text="Value:").grid(row=2, column=0, padx=5, pady=5)
    value_entry = tk.Entry(edit_window)
    value_entry.grid(row=2, column=1, padx=5, pady=5)
    value_entry.insert(0, asset[3])

    tk.Label(edit_window, text="Responsible Person:").grid(row=3, column=0, padx=5, pady=5)
    responsible_person_combobox = ttk.Combobox(edit_window, values=[emp[1] for emp in display_employees()])
    responsible_person_combobox.grid(row=3, column=1, padx=5, pady=5)
    responsible_person_combobox.set(asset[4])

    tk.Label(edit_window, text="Purchase Place:").grid(row=4, column=0, padx=5, pady=5)
    purchase_place_entry = tk.Entry(edit_window)
    purchase_place_entry.grid(row=4, column=1, padx=5, pady=5)
    purchase_place_entry.insert(0, asset[5])

    tk.Label(edit_window, text="City:").grid(row=5, column=0, padx=5, pady=5)
    city_entry = tk.Entry(edit_window)
    city_entry.grid(row=5, column=1, padx=5, pady=5)
    city_entry.insert(0, asset[6])

    tk.Label(edit_window, text="Street:").grid(row=6, column=0, padx=5, pady=5)
    street_entry = tk.Entry(edit_window)
    street_entry.grid(row=6, column=1, padx=5, pady=5)
    street_entry.insert(0, asset[7])

    tk.Label(edit_window, text="Building Number:").grid(row=7, column=0, padx=5, pady=5)
    building_number_entry = tk.Entry(edit_window)
    building_number_entry.grid(row=7, column=1, padx=5, pady=5)
    building_number_entry.insert(0, asset[8])

    tk.Label(edit_window, text="Room:").grid(row=8, column=0, padx=5, pady=5)
    room_entry = tk.Entry(edit_window)
    room_entry.grid(row=8, column=1, padx=5, pady=5)
    room_entry.insert(0, asset[9])

    tk.Label(edit_window, text="Date Received (DD-MM-YYYY):").grid(row=9, column=0, padx=5, pady=5)
    date_received_frame = tk.Frame(edit_window)
    date_received_frame.grid(row=9, column=1, padx=5, pady=5)

    day_var = tk.StringVar(value=asset[10].split('-')[0])
    month_var = tk.StringVar(value=asset[10].split('-')[1])
    year_var = tk.StringVar(value=asset[10].split('-')[2])

    tk.Entry(date_received_frame, textvariable=day_var, width=5, validate="key", validatecommand=(validate_day, "%P")).pack(side=tk.LEFT)
    tk.Label(date_received_frame, text="-").pack(side=tk.LEFT)
    tk.Entry(date_received_frame, textvariable=month_var, width=5, validate="key", validatecommand=(validate_month, "%P")).pack(side=tk.LEFT)
    tk.Label(date_received_frame, text="-").pack(side=tk.LEFT)
    tk.Entry(date_received_frame, textvariable=year_var, width=10, validate="key", validatecommand=(validate_year, "%P")).pack(side=tk.LEFT)

    def save_changes():
        new_name = name_entry.get()
        new_description = description_entry.get()
        new_value = value_entry.get()
        new_responsible_person = responsible_person_combobox.get()
        new_purchase_place = purchase_place_entry.get()
        new_city = city_entry.get()
        new_street = street_entry.get()
        new_building_number = building_number_entry.get()
        new_room = room_entry.get()
        new_date_received = f"{day_var.get()}-{month_var.get()}-{year_var.get()}"

        if new_name and new_value and new_city and new_street and new_building_number and new_room and day_var.get() and month_var.get() and year_var.get():
            update_asset(asset_id, new_name, new_description, new_value, new_responsible_person, new_purchase_place, new_city, new_street, new_building_number, new_room, new_date_received)
            messagebox.showinfo("Success", "Asset updated successfully")
            edit_window.destroy()
            updated_assets = display_assets()
            show_assets(updated_assets, title="Updated Asset List")

    tk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=10, column=0, columnspan=2, pady=10)

def edit_employee_command(employee):
    employee_id = employee[0]

    edit_window = Toplevel(root)
    edit_window.title("Edit Employee")

    tk.Label(edit_window, text="Name:").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(edit_window)
    name_entry.grid(row=0, column=1, padx=5, pady=5)
    name_entry.insert(0, employee[1])

    tk.Label(edit_window, text="Position:").grid(row=1, column=0, padx=5, pady=5)
    position_entry = tk.Entry(edit_window)
    position_entry.grid(row=1, column=1, padx=5, pady=5)
    position_entry.insert(0, employee[2])

    tk.Label(edit_window, text="Department:").grid(row=2, column=0, padx=5, pady=5)
    department_entry = tk.Entry(edit_window)
    department_entry.grid(row=2, column=1, padx=5, pady=5)
    if len(employee) > 4:
        department_entry.insert(0, employee[4])

    tk.Label(edit_window, text="Supervisor:").grid(row=3, column=0, padx=5, pady=5)
    supervisor_entry = tk.Entry(edit_window)
    supervisor_entry.grid(row=3, column=1, padx=5, pady=5)
    if len(employee) > 5:
        supervisor_entry.insert(0, employee[5])

    tk.Label(edit_window, text="Salary:").grid(row=4, column=0, padx=5, pady=5)
    salary_entry = tk.Entry(edit_window)
    salary_entry.grid(row=4, column=1, padx=5, pady=5)
    if len(employee) > 6:
        salary_entry.insert(0, employee[6])

    tk.Label(edit_window, text="Hire Date (DD-MM-YYYY):").grid(row=5, column=0, padx=5, pady=5)
    hire_date_frame = tk.Frame(edit_window)
    hire_date_frame.grid(row=5, column=1, padx=5, pady=5)

    emp_day_var = tk.StringVar(value=employee[3].split('-')[0])
    emp_month_var = tk.StringVar(value=employee[3].split('-')[1])
    emp_year_var = tk.StringVar(value=employee[3].split('-')[2])

    tk.Entry(hire_date_frame, textvariable=emp_day_var, width=5, validate="key", validatecommand=(validate_day, "%P")).pack(side=tk.LEFT)
    tk.Label(hire_date_frame, text="-").pack(side=tk.LEFT)
    tk.Entry(hire_date_frame, textvariable=emp_month_var, width=5, validate="key", validatecommand=(validate_month, "%P")).pack(side=tk.LEFT)
    tk.Label(hire_date_frame, text="-").pack(side=tk.LEFT)
    tk.Entry(hire_date_frame, textvariable=emp_year_var, width=10, validate="key", validatecommand=(validate_year, "%P")).pack(side=tk.LEFT)

    def save_changes():
        new_name = name_entry.get()
        new_position = position_entry.get()
        new_department = department_entry.get()
        new_supervisor = supervisor_entry.get()
        new_salary = salary_entry.get()
        new_hire_date = f"{emp_day_var.get()}-{emp_month_var.get()}-{emp_year_var.get()}"

        if new_name and new_position and new_department and new_salary and emp_day_var.get() and emp_month_var.get() and emp_year_var.get():
            update_employee(employee_id, new_name, new_position, new_hire_date, new_department, new_supervisor, new_salary)
            messagebox.showinfo("Success", "Employee updated successfully")
            edit_window.destroy()
            updated_employees = display_employees()
            show_employees(updated_employees, title="Updated Employee List")

    tk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=6, column=0, columnspan=2, pady=10)

def edit_asset_list():
    sort_by = sort_by_combobox.get()
    sort_order = sort_order_combobox.get()
    filters = {
        "name": name_filter_entry.get(),
        "description": description_filter_entry.get(),
        "value": value_filter_entry.get(),
        "responsible_person": responsible_person_filter_entry.get(),
        "purchase_place": purchase_place_filter_entry.get(),
        "city": city_filter_entry.get(),
        "street": street_filter_entry.get(),
        "building_number": building_number_filter_entry.get(),
        "room": room_filter_entry.get()
    }
    min_value = min_value_entry.get()
    max_value = max_value_entry.get()
    value_range = (min_value, max_value) if min_value and max_value else None

    start_day = start_day_var.get()
    start_month = start_month_var.get()
    start_year = start_year_var.get()
    end_day = end_day_var.get()
    end_month = end_month_var.get()
    end_year = end_year_var.get()

    start_date = f"{start_day}-{start_month}-{start_year}" if start_day and start_month and start_year else None
    end_date = f"{end_day}-{end_month}-{end_year}" if end_day and end_month and end_year else None

    date_range = (start_date, end_date) if start_date and end_date else None

    assets = display_assets(sort_by, sort_order, filters, value_range, date_range)
    show_assets(assets, title="Edit Asset List")
    if assets:
        asset_ids = [asset[0] for asset in assets]
        asset_id = simpledialog.askinteger("Input", "Enter the ID of the asset you want to edit:", initialvalue=asset_ids[0], minvalue=min(asset_ids), maxvalue=max(asset_ids))
        if asset_id:
            asset_to_edit = [asset for asset in assets if asset[0] == asset_id]
            if asset_to_edit:
                edit_asset_command(asset_to_edit[0])

def edit_employee_list():
    employees = display_employees()
    show_employees(employees, title="Edit Employee List")
    if employees:
        employee_ids = [employee[0] for employee in employees]
        employee_id = simpledialog.askinteger("Input", "Enter the ID of the employee you want to edit:", initialvalue=employee_ids[0], minvalue=min(employee_ids), maxvalue=max(employee_ids))
        if employee_id:
            employee_to_edit = [employee for employee in employees if employee[0] == employee_id]
            if employee_to_edit:
                edit_employee_command(employee_to_edit[0])

def delete_asset_command(asset):
    asset_id = asset[0]
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this asset?")
    if confirm:
        delete_asset(asset_id)
        messagebox.showinfo("Success", "Asset deleted successfully")
        updated_assets = display_assets()
        show_assets(updated_assets, title="Updated Asset List")

def delete_employee_command(employee):
    employee_id = employee[0]
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this employee?")
    if confirm:
        delete_employee(employee_id)
        messagebox.showinfo("Success", "Employee deleted successfully")
        updated_employees = display_employees()
        show_employees(updated_employees, title="Updated Employee List")

def delete_asset_list():
    sort_by = sort_by_combobox.get()
    sort_order = sort_order_combobox.get()
    filters = {
        "name": name_filter_entry.get(),
        "description": description_filter_entry.get(),
        "value": value_filter_entry.get(),
        "responsible_person": responsible_person_filter_entry.get(),
        "purchase_place": purchase_place_filter_entry.get(),
        "city": city_filter_entry.get(),
        "street": street_filter_entry.get(),
        "building_number": building_number_filter_entry.get(),
        "room": room_filter_entry.get()
    }
    min_value = min_value_entry.get()
    max_value = max_value_entry.get()
    value_range = (min_value, max_value) if min_value and max_value else None

    start_day = start_day_var.get()
    start_month = start_month_var.get()
    start_year = start_year_var.get()
    end_day = end_day_var.get()
    end_month = end_month_var.get()
    end_year = end_year_var.get()

    start_date = f"{start_day}-{start_month}-{start_year}" if start_day and start_month and start_year else None
    end_date = f"{end_day}-{end_month}-{end_year}" if end_day and end_month and end_year else None

    date_range = (start_date, end_date) if start_date and end_date else None

    assets = display_assets(sort_by, sort_order, filters, value_range, date_range)
    show_assets(assets, title="Delete Asset List")
    if assets:
        asset_ids = [asset[0] for asset in assets]
        asset_id = simpledialog.askinteger("Input", "Enter the ID of the asset you want to delete:", initialvalue=asset_ids[0], minvalue=min(asset_ids), maxvalue=max(asset_ids))
        if asset_id:
            asset_to_delete = [asset for asset in assets if asset[0] == asset_id]
            if asset_to_delete:
                delete_asset_command(asset_to_delete[0])

def delete_employee_list():
    employees = display_employees()
    show_employees(employees, title="Delete Employee List")
    if employees:
        employee_ids = [employee[0] for employee in employees]
        employee_id = simpledialog.askinteger("Input", "Enter the ID of the employee you want to delete:", initialvalue=employee_ids[0], minvalue=min(employee_ids), maxvalue=max(employee_ids))
        if employee_id:
            employee_to_delete = [employee for employee in employees if employee[0] == employee_id]
            if employee_to_delete:
                delete_employee_command(employee_to_delete[0])

def validate_value(P):
    if P.isdigit() or P == "":
        return True
    return False

def validate_day(P):
    if P.isdigit() and (1 <= int(P) <= 31 or P == ""):
        return True
    if P == "":
        return True
    return False

def validate_month(P):
    if P.isdigit() and (1 <= int(P) <= 12 or P == ""):
        return True
    if P == "":
        return True
    return False

def validate_year(P):
    if P.isdigit() and (1 <= int(P) <= 2024 or P == ""):
        return True
    if P == "":
        return True
    return False

def import_from_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if 'id' in reader.fieldnames:
                messagebox.showerror("Error", "CSV file contains 'id' column. Please remove it and try again.")
                return
            for row in reader:
                add_asset(
                    row['name'], row['description'], row['value'],
                    row['responsible_person'], row['purchase_place'],
                    row['city'], row['street'], row['building_number'], row['room'], row['date_received']
                )
        messagebox.showinfo("Success", "Data imported successfully")

def export_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        assets = display_assets()
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'name', 'description', 'value', 'responsible_person', 'purchase_place', 'city', 'street', 'building_number', 'room', 'date_received']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for asset in assets:
                writer.writerow({
                    'id': asset[0],
                    'name': asset[1],
                    'description': asset[2],
                    'value': asset[3],
                    'responsible_person': asset[4],
                    'purchase_place': asset[5],
                    'city': asset[6],
                    'street': asset[7],
                    'building_number': asset[8],
                    'room': asset[9],
                    'date_received': asset[10]
                })
        messagebox.showinfo("Success", "Data exported successfully")

def import_employees_from_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if 'id' in reader.fieldnames:
                messagebox.showerror("Error", "CSV file contains 'id' column. Please remove it and try again.")
                return
            for row in reader:
                add_employee(
                    row['name'], row['position'], row['hire_date'], row['department'], row['supervisor'], row['salary']
                )
        messagebox.showinfo("Success", "Employee data imported successfully")

def export_employees_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        employees = display_employees()
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'name', 'position', 'hire_date', 'department', 'supervisor', 'salary']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for employee in employees:
                writer.writerow({
                    'id': employee[0],
                    'name': employee[1],
                    'position': employee[2],
                    'hire_date': employee[3],
                    'department': employee[4] if len(employee) > 4 else '',
                    'supervisor': employee[5] if len(employee) > 5 else '',
                    'salary': employee[6] if len(employee) > 6 else ''
                })
        messagebox.showinfo("Success", "Employee data exported successfully")

def show_frame(frame):
    frame.tkraise()

# Database initialization
create_tables()

# GUI creation
root = tk.Tk()
root.title("Management System")
root.geometry("600x800")

# Define frames
menu_frame = tk.Frame(root)
asset_management_frame = tk.Frame(root)
employee_management_frame = tk.Frame(root)
add_asset_frame = tk.Frame(root)
edit_asset_frame = tk.Frame(root)
delete_asset_frame = tk.Frame(root)
display_asset_frame = tk.Frame(root)
add_employee_frame = tk.Frame(root)
edit_employee_frame = tk.Frame(root)
delete_employee_frame = tk.Frame(root)

for frame in (menu_frame, asset_management_frame, employee_management_frame, add_asset_frame, edit_asset_frame, delete_asset_frame, display_asset_frame, add_employee_frame, edit_employee_frame, delete_employee_frame):
    frame.grid(row=0, column=0, sticky='nsew')

# Menu frame
tk.Label(menu_frame, text="Management System", font=("Helvetica", 16)).pack(pady=20)
tk.Button(menu_frame, text="Asset Management", command=lambda: show_frame(asset_management_frame)).pack(pady=10)
tk.Button(menu_frame, text="Employee Management", command=lambda: show_frame(employee_management_frame)).pack(pady=10)
tk.Button(menu_frame, text="Close Program", command=root.quit).pack(pady=10)

# Asset management frame
tk.Label(asset_management_frame, text="Asset Management", font=("Helvetica", 16)).pack(pady=20)
tk.Button(asset_management_frame, text="Add New Asset", command=lambda: show_frame(add_asset_frame)).pack(pady=10)
tk.Button(asset_management_frame, text="Edit Asset", command=lambda: show_frame(edit_asset_frame)).pack(pady=10)
tk.Button(asset_management_frame, text="Delete Asset", command=lambda: show_frame(delete_asset_frame)).pack(pady=10)
tk.Button(asset_management_frame, text="Display Assets", command=lambda: show_frame(display_asset_frame)).pack(pady=10)
tk.Button(asset_management_frame, text="Import Assets from CSV", command=import_from_csv).pack(pady=10)
tk.Button(asset_management_frame, text="Export Assets to CSV", command=export_to_csv).pack(pady=10)
tk.Button(asset_management_frame, text="Back to Menu", command=lambda: show_frame(menu_frame)).pack(pady=10)

# Employee management frame
tk.Label(employee_management_frame, text="Employee Management", font=("Helvetica", 16)).pack(pady=20)
tk.Button(employee_management_frame, text="Add New Employee", command=lambda: show_frame(add_employee_frame)).pack(pady=10)
tk.Button(employee_management_frame, text="Edit Employee", command=lambda: show_frame(edit_employee_frame)).pack(pady=10)
tk.Button(employee_management_frame, text="Delete Employee", command=lambda: show_frame(delete_employee_frame)).pack(pady=10)
tk.Button(employee_management_frame, text="Display Employees", command=display_employees_command).pack(pady=10)
tk.Button(employee_management_frame, text="Import Employees from CSV", command=import_employees_from_csv).pack(pady=10)
tk.Button(employee_management_frame, text="Export Employees to CSV", command=export_employees_to_csv).pack(pady=10)
tk.Button(employee_management_frame, text="Back to Menu", command=lambda: show_frame(menu_frame)).pack(pady=10)

# Add asset frame
tk.Label(add_asset_frame, text="Add New Asset", font=("Helvetica", 16)).pack(pady=20)
add_asset_form = tk.Frame(add_asset_frame)
add_asset_form.pack(pady=10)

validate_cmd = add_asset_form.register(validate_value)
validate_day_cmd = add_asset_form.register(validate_day)
validate_month_cmd = add_asset_form.register(validate_month)
validate_year_cmd = add_asset_form.register(validate_year)

tk.Label(add_asset_form, text="Name *:").grid(row=0, column=0, padx=5, pady=5)
name_entry = tk.Entry(add_asset_form)
name_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(add_asset_form, text="Description:").grid(row=1, column=0, padx=5, pady=5)
description_entry = tk.Entry(add_asset_form)
description_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(add_asset_form, text="Value *:").grid(row=2, column=0, padx=5, pady=5)
value_entry = tk.Entry(add_asset_form, validate="key", validatecommand=(validate_cmd, "%P"))
value_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(add_asset_form, text="Responsible Person:").grid(row=3, column=0, padx=5, pady=5)
responsible_person_combobox = ttk.Combobox(add_asset_form, values=[emp[1] for emp in display_employees()])
responsible_person_combobox.grid(row=3, column=1, padx=5, pady=5)

tk.Label(add_asset_form, text="Purchase Place:").grid(row=4, column=0, padx=5, pady=5)
purchase_place_entry = tk.Entry(add_asset_form)
purchase_place_entry.grid(row=4, column=1, padx=5, pady=5)

tk.Label(add_asset_form, text="City *:").grid(row=5, column=0, padx=5, pady=5)
city_entry = tk.Entry(add_asset_form)
city_entry.grid(row=5, column=1, padx=5, pady=5)

tk.Label(add_asset_form, text="Street *:").grid(row=6, column=0, padx=5, pady=5)
street_entry = tk.Entry(add_asset_form)
street_entry.grid(row=6, column=1, padx=5, pady=5)

tk.Label(add_asset_form, text="Building Number *:").grid(row=7, column=0, padx=5, pady=5)
building_number_entry = tk.Entry(add_asset_form)
building_number_entry.grid(row=7, column=1, padx=5, pady=5)

tk.Label(add_asset_form, text="Room *:").grid(row=8, column=0, padx=5, pady=5)
room_entry = tk.Entry(add_asset_form)
room_entry.grid(row=8, column=1, padx=5, pady=5)

tk.Label(add_asset_form, text="Date Received * (DD-MM-YYYY):").grid(row=9, column=0, padx=5, pady=5)
date_received_frame = tk.Frame(add_asset_form)
date_received_frame.grid(row=9, column=1, padx=5, pady=5)

day_var = tk.StringVar()
month_var = tk.StringVar()
year_var = tk.StringVar()

tk.Entry(date_received_frame, textvariable=day_var, width=5, validate="key", validatecommand=(validate_day_cmd, "%P")).pack(side=tk.LEFT)
tk.Label(date_received_frame, text="-").pack(side=tk.LEFT)
tk.Entry(date_received_frame, textvariable=month_var, width=5, validate="key", validatecommand=(validate_month_cmd, "%P")).pack(side=tk.LEFT)
tk.Label(date_received_frame, text="-").pack(side=tk.LEFT)
tk.Entry(date_received_frame, textvariable=year_var, width=10, validate="key", validatecommand=(validate_year_cmd, "%P")).pack(side=tk.LEFT)

tk.Button(add_asset_form, text="Add Asset", command=add_asset_command).grid(row=10, column=0, columnspan=2, pady=10)
tk.Label(add_asset_form, text="* Mandatory fields", fg="red").grid(row=11, column=0, columnspan=2)
tk.Button(add_asset_form, text="Back to Menu", command=lambda: show_frame(asset_management_frame)).grid(row=12, column=0, columnspan=2, pady=10)

# Add employee frame
tk.Label(add_employee_frame, text="Add New Employee", font=("Helvetica", 16)).pack(pady=20)
add_employee_form = tk.Frame(add_employee_frame)
add_employee_form.pack(pady=10)

tk.Label(add_employee_form, text="Name *:").grid(row=0, column=0, padx=5, pady=5)
employee_name_entry = tk.Entry(add_employee_form)
employee_name_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(add_employee_form, text="Position *:").grid(row=1, column=0, padx=5, pady=5)
employee_position_entry = tk.Entry(add_employee_form)
employee_position_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(add_employee_form, text="Department *:").grid(row=2, column=0, padx=5, pady=5)
employee_department_entry = tk.Entry(add_employee_form)
employee_department_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(add_employee_form, text="Supervisor:").grid(row=3, column=0, padx=5, pady=5)
employee_supervisor_entry = tk.Entry(add_employee_form)
employee_supervisor_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Label(add_employee_form, text="Salary *:").grid(row=4, column=0, padx=5, pady=5)
employee_salary_entry = tk.Entry(add_employee_form)
employee_salary_entry.grid(row=4, column=1, padx=5, pady=5)

tk.Label(add_employee_form, text="Hire Date * (DD-MM-YYYY):").grid(row=5, column=0, padx=5, pady=5)
employee_hire_date_frame = tk.Frame(add_employee_form)
employee_hire_date_frame.grid(row=5, column=1, padx=5, pady=5)

emp_day_var = tk.StringVar()
emp_month_var = tk.StringVar()
emp_year_var = tk.StringVar()

tk.Entry(employee_hire_date_frame, textvariable=emp_day_var, width=5, validate="key", validatecommand=(validate_day_cmd, "%P")).pack(side=tk.LEFT)
tk.Label(employee_hire_date_frame, text="-").pack(side=tk.LEFT)
tk.Entry(employee_hire_date_frame, textvariable=emp_month_var, width=5, validate="key", validatecommand=(validate_month_cmd, "%P")).pack(side=tk.LEFT)
tk.Label(employee_hire_date_frame, text="-").pack(side=tk.LEFT)
tk.Entry(employee_hire_date_frame, textvariable=emp_year_var, width=10, validate="key", validatecommand=(validate_year_cmd, "%P")).pack(side=tk.LEFT)

tk.Button(add_employee_form, text="Add Employee", command=add_employee_command).grid(row=6, column=0, columnspan=2, pady=10)
tk.Label(add_employee_form, text="* Mandatory fields", fg="red").grid(row=7, column=0, columnspan=2)
tk.Button(add_employee_form, text="Back to Menu", command=lambda: show_frame(employee_management_frame)).grid(row=8, column=0, columnspan=2, pady=10)

# Edit asset frame
tk.Label(edit_asset_frame, text="Edit Asset", font=("Helvetica", 16)).pack(pady=20)
tk.Button(edit_asset_frame, text="Edit Asset List", command=edit_asset_list).pack(pady=10)
tk.Button(edit_asset_frame, text="Back to Menu", command=lambda: show_frame(asset_management_frame)).pack(pady=10)

# Edit employee frame
tk.Label(edit_employee_frame, text="Edit Employee", font=("Helvetica", 16)).pack(pady=20)
tk.Button(edit_employee_frame, text="Edit Employee List", command=edit_employee_list).pack(pady=10)
tk.Button(edit_employee_frame, text="Back to Menu", command=lambda: show_frame(employee_management_frame)).pack(pady=10)

# Delete asset frame
tk.Label(delete_asset_frame, text="Delete Asset", font=("Helvetica", 16)).pack(pady=20)
tk.Button(delete_asset_frame, text="Delete Asset List", command=delete_asset_list).pack(pady=10)
tk.Button(delete_asset_frame, text="Back to Menu", command=lambda: show_frame(asset_management_frame)).pack(pady=10)

# Delete employee frame
tk.Label(delete_employee_frame, text="Delete Employee", font=("Helvetica", 16)).pack(pady=20)
tk.Button(delete_employee_frame, text="Delete Employee List", command=delete_employee_list).pack(pady=10)
tk.Button(delete_employee_frame, text="Back to Menu", command=lambda: show_frame(employee_management_frame)).pack(pady=10)

# Display assets frame
tk.Label(display_asset_frame, text="Display Assets", font=("Helvetica", 16)).pack(pady=20)
filter_frame = tk.Frame(display_asset_frame)
filter_frame.pack(pady=10)

tk.Label(filter_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
name_filter_entry = tk.Entry(filter_frame)
name_filter_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(filter_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5)
description_filter_entry = tk.Entry(filter_frame)
description_filter_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(filter_frame, text="Value:").grid(row=2, column=0, padx=5, pady=5)
value_filter_entry = tk.Entry(filter_frame)
value_filter_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(filter_frame, text="Value Range:").grid(row=3, column=0, padx=5, pady=5)
tk.Label(filter_frame, text="Min:").grid(row=3, column=1, padx=5, pady=5)
min_value_entry = tk.Entry(filter_frame)
min_value_entry.grid(row=3, column=2, padx=5, pady=5)
tk.Label(filter_frame, text="Max:").grid(row=3, column=3, padx=5, pady=5)
max_value_entry = tk.Entry(filter_frame)
max_value_entry.grid(row=3, column=4, padx=5, pady=5)

tk.Label(filter_frame, text="Responsible Person:").grid(row=4, column=0, padx=5, pady=5)
responsible_person_filter_entry = tk.Entry(filter_frame)
responsible_person_filter_entry.grid(row=4, column=1, padx=5, pady=5)

tk.Label(filter_frame, text="Purchase Place:").grid(row=5, column=0, padx=5, pady=5)
purchase_place_filter_entry = tk.Entry(filter_frame)
purchase_place_filter_entry.grid(row=5, column=1, padx=5, pady=5)

tk.Label(filter_frame, text="City:").grid(row=6, column=0, padx=5, pady=5)
city_filter_entry = tk.Entry(filter_frame)
city_filter_entry.grid(row=6, column=1, padx=5, pady=5)

tk.Label(filter_frame, text="Street:").grid(row=7, column=0, padx=5, pady=5)
street_filter_entry = tk.Entry(filter_frame)
street_filter_entry.grid(row=7, column=1, padx=5, pady=5)

tk.Label(filter_frame, text="Building Number:").grid(row=8, column=0, padx=5, pady=5)
building_number_filter_entry = tk.Entry(filter_frame)
building_number_filter_entry.grid(row=8, column=1, padx=5, pady=5)

tk.Label(filter_frame, text="Room:").grid(row=9, column=0, padx=5, pady=5)
room_filter_entry = tk.Entry(filter_frame)
room_filter_entry.grid(row=9, column=1, padx=5, pady=5)

tk.Label(filter_frame, text="Start Date (DD-MM-YYYY):").grid(row=10, column=0, padx=5, pady=5)
start_date_frame = tk.Frame(filter_frame)
start_date_frame.grid(row=10, column=1, padx=5, pady=5)

start_day_var = tk.StringVar()
start_month_var = tk.StringVar()
start_year_var = tk.StringVar()

tk.Entry(start_date_frame, textvariable=start_day_var, width=5, validate="key", validatecommand=(validate_day_cmd, "%P")).pack(side=tk.LEFT)
tk.Label(start_date_frame, text="-").pack(side=tk.LEFT)
tk.Entry(start_date_frame, textvariable=start_month_var, width=5, validate="key", validatecommand=(validate_month_cmd, "%P")).pack(side=tk.LEFT)
tk.Label(start_date_frame, text="-").pack(side=tk.LEFT)
tk.Entry(start_date_frame, textvariable=start_year_var, width=10, validate="key", validatecommand=(validate_year_cmd, "%P")).pack(side=tk.LEFT)

tk.Label(filter_frame, text="End Date (DD-MM-YYYY):").grid(row=11, column=0, padx=5, pady=5)
end_date_frame = tk.Frame(filter_frame)
end_date_frame.grid(row=11, column=1, padx=5, pady=5)

end_day_var = tk.StringVar()
end_month_var = tk.StringVar()
end_year_var = tk.StringVar()

tk.Entry(end_date_frame, textvariable=end_day_var, width=5, validate="key", validatecommand=(validate_day_cmd, "%P")).pack(side=tk.LEFT)
tk.Label(end_date_frame, text="-").pack(side=tk.LEFT)
tk.Entry(end_date_frame, textvariable=end_month_var, width=5, validate="key", validatecommand=(validate_month_cmd, "%P")).pack(side=tk.LEFT)
tk.Label(end_date_frame, text="-").pack(side=tk.LEFT)
tk.Entry(end_date_frame, textvariable=end_year_var, width=10, validate="key", validatecommand=(validate_year_cmd, "%P")).pack(side=tk.LEFT)

tk.Label(filter_frame, text="Sort By:").grid(row=12, column=0, padx=5, pady=5)
sort_by_combobox = ttk.Combobox(filter_frame, values=["id", "name", "description", "value", "responsible_person", "purchase_place", "city", "street", "building_number", "room", "date_received"])
sort_by_combobox.grid(row=12, column=1, padx=5, pady=5)

tk.Label(filter_frame, text="Sort Order:").grid(row=13, column=0, padx=5, pady=5)
sort_order_combobox = ttk.Combobox(filter_frame, values=["ASC", "DESC"])
sort_order_combobox.grid(row=13, column=1, padx=5, pady=5)

tk.Button(filter_frame, text="Display Assets", command=display_assets_command).grid(row=14, column=0, columnspan=2, pady=10)
tk.Button(display_asset_frame, text="Back to Menu", command=lambda: show_frame(asset_management_frame)).pack(pady=10)

# Start with menu frame
show_frame(menu_frame)

# Start the GUI event loop
root.mainloop()

