{
  "type": "ForexVolatility",
  "name": "FQP",
  "conditions": [
    {
      "id": "Currency_1",
      "label": "Currency_1"
    },
    {
      "id": "Currency_2",
      "label": "Currency_2"
    }
  ],
  "consequences": [
    {
      "id": "VolatilityCurve",
      "label": "Volatility Curve"
    }
  ],
  "rows": [
    {
      "Currency_1": "Currency_1='$id/EUR'",
      "Currency_2": "Currency_2='$id/USD'",
      "VolatilityCurve": "VolatilityCurve = '$id/EUR_USD_VolSurf'"
    },
    {
      "Currency_1": "Currency_1='$id/EUR'",
      "Currency_2": "Currency_2='$id/JPY'",
      "VolatilityCurve": "VolatilityCurve = '$id/EUR_JPY_VolSurf'"
    },
    {
      "Currency_1": "Currency_1='$id/EUR'",
      "Currency_2": "Currency_2='$id/GBP'",
      "VolatilityCurve": "VolatilityCurve = '$id/EUR_GBP_VolSurf'"
    },
    {
      "Currency_1": "Currency_1='$id/EUR'",
      "Currency_2": "Currency_2='$id/HKD'",
      "VolatilityCurve": "VolatilityCurve = '$id/EUR_HKD_VolSurf'"
    },
    {
      "Currency_1": "Currency_1='$id/USD'",
      "Currency_2": "Currency_2='$id/JPY'",
      "VolatilityCurve": "VolatilityCurve = '$id/USD_JPY_VolSurf'"
    },
    {
      "Currency_1": "Currency_1='$id/GBP'",
      "Currency_2": "Currency_2='$id/USD'",
      "VolatilityCurve": "VolatilityCurve = '$id/GBP_USD_VolSurf'"
    },
    {
      "Currency_1": "Currency_1='$id/CAD'",
      "Currency_2": "Currency_2='$id/JPY'",
      "VolatilityCurve": "VolatilityCurve = '$id/CAD_JPY_VolSurf'"
    }
  ]
}