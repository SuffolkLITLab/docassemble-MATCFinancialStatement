import os
from distutils.util import convert_path
from fnmatch import fnmatchcase

from setuptools import find_namespace_packages, setup

standard_exclude = ("*.pyc", "*~", ".*", "*.bak", "*.swp*")
standard_exclude_directories = (".*", "CVS", "_darcs", "./build", "./dist", "EGG-INFO", "*.egg-info")


def find_package_data(where=".", package="", exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), "", package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if fnmatchcase(name, pattern) or fn.lower() == pattern.lower():
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, "__init__.py")):
                    new_package = name if not package else package + "." + name
                    stack.append((fn, "", new_package))
                else:
                    stack.append((fn, prefix + name + "/", package))
            else:
                bad_name = False
                for pattern in exclude:
                    if fnmatchcase(name, pattern) or fn.lower() == pattern.lower():
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix + name)
    return out


setup(
    name="docassemble.MATCFinancialStatement",
    version="1.48",
    description="A docassemble interview for Massachusetts financial statement forms.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Court Forms Online",
    author_email="litlab@suffolk.edu",
    license="MIT",
    url="https://courtformsonline.org",
    packages=find_namespace_packages(include=["docassemble*"]),
    install_requires=[
        "docassemble.ALMassachusetts>=0.1.2",
        "docassemble.AssemblyLine @ git+https://github.com/SuffolkLITLab/docassemble-AssemblyLine.git@main",
        "docassemble.MassAccess @ git+https://github.com/SuffolkLITLab/docassemble-MassAccess.git@main",
        "docassemble.ALToolbox @ git+https://github.com/SuffolkLITLab/docassemble-ALToolbox.git@main",
    ],
    zip_safe=False,
    package_data=find_package_data(
        where="docassemble/MATCFinancialStatement/",
        package="docassemble.MATCFinancialStatement",
    ),
)
