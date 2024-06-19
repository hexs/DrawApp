from os import makedirs
from os.path import join

path = join("C:\\", "PythonProjects")
makedirs(path, exist_ok=True)
path = join(path, "Test folder2")
makedirs(path, exist_ok=True)



import os
# path = (os.path.join("C:", "PythonProjects", "Test folder2"))
# os.makedirs(path,exist_ok=True)