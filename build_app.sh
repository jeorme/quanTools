py setup.py sdist --formats=gztar
py setup.py build
py setup.py install
cf login -a api.eu-gb.bluemix.net -u jerome.petit@outlook.com -p Jeorme79$
cf push pricerV1 -m 256M