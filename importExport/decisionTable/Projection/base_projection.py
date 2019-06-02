{
  "type": "Projection",
  "name": "FQP",
  "conditions": [
    {
      "id": "Currency",
      "label": "Currency"
    },
    {
      "id": "Term",
      "label": "Term"
    }
  ],
  "consequences": [
    {
      "id": "YieldCurve",
      "label": "Yield Curve"
    }
  ],
  "rows": [
    {
      "Currency": "Currency = '$id/USD'",
      "Term": "Term = '1BD'",
      "YieldCurve": "YieldCurve = '$id/USDOIS'"
    },
    {
      "Currency": "Currency = '$id/USD'",
      "Term": "Term = '1M'",
      "YieldCurve": "YieldCurve = '$id/USDSBML'"
    },
    {
      "Currency": "Currency = '$id/USD'",
      "Term": "Term = '3M'",
      "YieldCurve": "YieldCurve = '$id/USDSBQL'"
    },
    {
      "Currency": "Currency = '$id/USD'",
      "Term": "Term = '6M'",
      "YieldCurve": "YieldCurve = '$id/USDSBSL'"
    },
    {
      "Currency": "Currency = '$id/EUR'",
      "Term": "Term = '1BD'",
      "YieldCurve": "YieldCurve = '$id/EUROIS'"
    },
    {
      "Currency": "Currency = '$id/EUR'",
      "Term": "Term = '1M'",
      "YieldCurve": "YieldCurve = '$id/EURAMME'"
    },
    {
      "Currency": "Currency = '$id/EUR'",
      "Term": "Term = '3M'",
      "YieldCurve": "YieldCurve = '$id/EURABQE'"
    },
    {
      "Currency": "Currency = '$id/EUR'",
      "Term": "Term = '6M'",
      "YieldCurve": "YieldCurve = '$id/EURABSE'"
    },
    {
      "Currency": "Currency = '$id/EUR'",
      "Term": "Term = '8M'",
      "YieldCurve": "YieldCurve = '$id/EURABSE'"
    },
    {
      "Currency": "Currency = '$id/EUR'",
      "Term": "Term = '9M'",
      "YieldCurve": "YieldCurve = '$id/EURABSE'"
    },
    {
      "Currency": "Currency = '$id/EUR'",
      "Term": "Term = '1Y'",
      "YieldCurve": "YieldCurve = '$id/EURABAE'"
    },
    {
      "Currency": "Currency = '$id/EUR'",
      "Term": "Term = '2Y'",
      "YieldCurve": "YieldCurve = '$id/EURABAE'"
    },
    {
      "Currency": "Currency = '$id/GBP'",
      "Term": "Term = '1BD'",
      "YieldCurve": "YieldCurve = '$id/GBPOIS'"
    },
    {
      "Currency": "Currency = '$id/GBP'",
      "Term": "Term = '3M'",
      "YieldCurve": "YieldCurve = '$id/GBPSBQL'"
    },
    {
      "Currency": "Currency = '$id/GBP'",
      "Term": "Term = '6M'",
      "YieldCurve": "YieldCurve = '$id/GBPSBSL'"
    },
    {
      "Currency": "Currency = '$id/MXN'",
      "YieldCurve": "YieldCurve = '$id/MXNOIS'"
    },
    {
      "Currency": "Currency = '$id/JPY'",
      "Term": "Term = '3M'",
      "YieldCurve": "YieldCurve = '$id/JPYSBQL'"
    },
    {
      "Currency": "Currency = '$id/JPY'",
      "Term": "Term = '6M'",
      "YieldCurve": "YieldCurve = '$id/JPYSBSL'"
    },
    {
      "Currency": "Currency = '$id/CHF'",
      "Term": "Term = '3M'",
      "YieldCurve": "YieldCurve = '$id/CHFAMQL'"
    },
    {
      "Currency": "Currency = '$id/CHF'",
      "Term": "Term = '6M'",
      "YieldCurve": "YieldCurve = '$id/CHFABSL'"
    },
    {
      "Currency": "Currency = '$id/HKD'",
      "YieldCurve": "YieldCurve = '$id/HKDQMSH'"
    },
    {
      "Currency": "Currency = '$id/CAD'",
      "YieldCurve": "YieldCurve = '$id/CAD-LIBOR'"
    }
  ]
}