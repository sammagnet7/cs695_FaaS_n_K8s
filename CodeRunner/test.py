import os


def create_directory(directory_path):
    # Get the directory of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Create the full path for the new directory
    new_directory_path = os.path.join(script_directory, directory_path)

    # Check if the directory already exists
    if not os.path.exists(new_directory_path):
        os.makedirs(new_directory_path)


# Example usage
directory_name = "my_directory"
create_directory(directory_name)
