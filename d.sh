#!dsh

# prepare environment
# pip install --upgrade build
# py -m pip install --upgrade twine


# increase version
# ... manuallly

# build
# py -m build




# deploy in test server
# py -m twine upload --repository testpypi dist/*

# install from test
# py -m pip install --index-url https://test.pypi.org/simple/ --no-deps -U dprojects_xmenu






# deploy in prod server
# py -m twine upload dist/*

# install from test
# py -m pip install --index-url https://test.pypi.org/simple/ --no-deps -U xmenu

echo 123