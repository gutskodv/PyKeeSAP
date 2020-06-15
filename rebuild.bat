python setup.py sdist bdist_wheel
FOR %%i IN ("dist\*.whl") DO Set FileName="%%i"
pip install %FileName% --force