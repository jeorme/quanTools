from flask_restplus import Api

from .rnn import api as rnn
from .pricer import api as pricer
from .trade import api as trade
from .timeseries import api as timeseries
from .bucket import api as bucket
from .cloudObject import api as cloudObject


api = Api(
    title='Quantitative tools',
    version='1.0',
    description='quantitative tools for pricing / calibrating / time series analysis',
    # All API metadatas
)

api.add_namespace(bucket)
api.add_namespace(cloudObject)
api.add_namespace(timeseries)
api.add_namespace(rnn)
