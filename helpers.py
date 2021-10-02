import getpass

# Bot say hello string template
def say_hello_str():
    os_username = getpass.getuser()
    return f"Greetings to you, {os_username} \r\n\n"

def get_user_name():
    user_name = getpass.getuser()
    arr = user_name.split(" ")
    if len(arr) > 2:
        user_name = f"{arr[0]} {arr[len(arr) - 1]}"

    return user_name
