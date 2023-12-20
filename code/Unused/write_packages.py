import pkg_resources

# Getting the list of installed packages
installed_packages = [f"{p.project_name}=={p.version}" for p in pkg_resources.working_set]

# File path for 'requirements.txt'
file_path = './requirements.txt'

# Writing the packages to the file
with open(file_path, 'w') as file:
    for package in installed_packages:
        file.write(package + "\n")
