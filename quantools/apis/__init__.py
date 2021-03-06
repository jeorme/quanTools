from flask_restplus import Api

from .timeseries import api as timeseries
from .pricing import api as pricing
from .calibration import api as calibration
from .interpolation import api as interpolation
from .analyticsTools import api as analytics
from .mock import api as mock
from .performance import api as performance
from .openData import api as openData

api = Api(
    title='Quantitative tools',
    version='1.1',
    description='quantitative tools for pricing / calibrating / time series analysis',
    # All API metadatas
)

api.add_namespace(timeseries)
api.add_namespace(pricing)
api.add_namespace(calibration)
api.add_namespace(interpolation)
api.add_namespace(analytics)
api.add_namespace(mock)
api.add_namespace(performance)
api.add_namespace(openData)

