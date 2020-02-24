py setup.py sdist
py setup.py build
py setup.py install
cf push priceV1 -m 256M