import sqlite3

def view_users():
    # Connect to the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Query to select all users
    cursor.execute("SELECT * FROM users")

    # Fetch all rows
    users = cursor.fetchall()

    # Display users
    if users:
        print("Users in the table:")
        for user in users:
            print(user)
    else:
        print("No users found in the table.")

    # Close the connection
    conn.close()

# Call the function
view_users()
