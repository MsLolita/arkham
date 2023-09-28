import subprocess
import pkgutil


class LibraryInstaller:
    def __init__(self, requirements_file: str):
        self.requirements_file = requirements_file

    @staticmethod
    def check_library(library):
        library = library.split("=")[0]
        if "-" in library:
            return pkgutil.find_loader(library.replace("-", "_")) or pkgutil.find_loader(library.replace("-", ""))
        return pkgutil.find_loader(library)

    def get_libraries(self):
        with open(self.requirements_file) as f:
            libraries = f.read().splitlines()
        return libraries

    def install_libraries(self):
        try:
            libraries = self.get_libraries()
            installed_libraries = [library for library in libraries if LibraryInstaller.check_library(library)]
            libraries_to_install = list(set(libraries) - set(installed_libraries))
            if libraries_to_install:
                print(libraries_to_install)
                subprocess.check_call(['pip', 'install', *libraries_to_install])
                print("\nAll required libraries are installed.")
        except FileNotFoundError:
            print(f"Error: {self.requirements_file} not found. Can't automatically install libraries.")

