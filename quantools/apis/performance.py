import functools
import json
import multiprocessing
import timeit

from dateutil.parser import parse
from flask import request, jsonify
import numpy as np
from flask_restplus import Namespace, Resource, fields

from quantools.library.fxvolCalibration.fxVol import constructFXVolSurface, calib1FxVol
from quantools.library.fxvolCalibration.outputRestService import outputFxVolCalibrated
from quantools.model.fxVolModel.fxVolPerformance import MdPerf
from quantools.model.fxVolModel.fxVolPerformance2 import MdDefPerf

api = Namespace('performance', 'performance mesure of the service exposed')


@api.route('/')
class FxVolPerFormance(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("fx vol calibration performance",{
        "marketData" : fields.Raw(example=MdPerf,type="json"),
        "asOfDate": fields.String(default="2011-02-02"),
        "marketDataDefinitions": fields.Raw(example=MdDefPerf,type="json")}))
    def post(self):
        """
        interpolation : smile axis
        :return: the interpolated value
        """

        # All the program statements
        start_json = timeit.default_timer()
        content = request.get_json()
        stop_json = timeit.default_timer()
        start_calib = timeit.default_timer()
        surface = constructFXVolSurface(content)
        stop_calib = timeit.default_timer()
        # define model
        start_output = timeit.default_timer()
        output =  outputFxVolCalibrated(surface, content)
        stop_output = timeit.default_timer()
        nb_surface = len(content["marketDataDefinitions"]["fxVolatilities"])

        expiry = [len(fxvol["expiries"]) for fxvol in content["marketDataDefinitions"]["fxVolatilities"] ]
        return jsonify({"nb Surface" : nb_surface, "nb expiry per curve" : json.dumps(expiry),"nb total expiry" : int(np.sum(expiry)),"total" : stop_output-start_json,"parsing input" : stop_json-start_json,"calibration : " : stop_calib-start_calib, "paring output : ": stop_output-start_output })


@api.route('/multicore')
class FxVolPerFormanceMC(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("fx vol calibration performance",{
        "marketData" : fields.Raw(example=MdPerf,type="json"),
        "asOfDate": fields.String(default="2011-02-02"),
        "marketDataDefinitions": fields.Raw(example=MdDefPerf,type="json")}))
    def post(self):
        """
        interpolation : smile axis
        :return: the interpolated value
        """

        # All the program statements
        start_json = timeit.default_timer()
        content = request.get_json()
        stop_json = timeit.default_timer()
        start_MCBuilding = timeit.default_timer()
        calib1FxVolMC = functools.partial(calib1FxVol, parse(content["asOfDate"]), content["marketData"],
                                          content["marketDataDefinitions"]["yieldCurves"])
        pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
        end_MCBuilding = timeit.default_timer()
        start_calib = timeit.default_timer()
        surface = pool.starmap(calib1FxVolMC, zip(content["marketDataDefinitions"]["fxVolatilities"]))
        pool.close()
        pool.join()
        pool.terminate()
        stop_calib = timeit.default_timer()
        # define model
        start_output = timeit.default_timer()
        output =  outputFxVolCalibrated(surface, content)
        stop_output = timeit.default_timer()
        nb_surface = len(content["marketDataDefinitions"]["fxVolatilities"])

        expiry = [len(fxvol["expiries"]) for fxvol in content["marketDataDefinitions"]["fxVolatilities"] ]
        return jsonify({"nb Surface" : nb_surface, "nb expiry per curve" : json.dumps(expiry),"nb total expiry" : int(np.sum(expiry)),"total" : stop_output-start_json,"parsing input" : stop_json-start_json,"multicore setting": end_MCBuilding -start_MCBuilding,"calibration : " : stop_calib-start_calib, "paring output : ": stop_output-start_output })