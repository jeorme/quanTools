{
  "type": "Discount",
  "name": "FQP",
  "conditions": [
    {
      "id": "Currency",
      "label": "Currency"
    },
    {
      "id": "CollateralCurrency",
      "label": "Collateral Currency"
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
      "Currency": "Currency = '$id/EUR'",
      "YieldCurve": "YieldCurve = '$id/EUROIS'"
    },
    {
      "Currency": "Currency = '$id/GBP'",
      "YieldCurve": "YieldCurve = '$id/GBPOIS'"
    },
    {
      "Currency": "Currency = '$id/USD'",
      "YieldCurve": "YieldCurve = '$id/USDOIS'"
    },
    {
      "Currency": "Currency = '$id/MXN'",
      "YieldCurve": "YieldCurve = '$id/MXNOIS'"
    },
    {
      "Currency": "Currency = '$id/CLP'",
      "YieldCurve": "YieldCurve = '$id/CLPGOV'"
    },
    {
      "Currency": "Currency = '$id/UDI'",
      "YieldCurve": "YieldCurve = '$id/UDISBMT'"
    },
    {
      "Currency": "Currency = '$id/JPY'",
      "CollateralCurrency": "CollateralCurrency = '$id/USD'",
      "YieldCurve": "YieldCurve = '$id/JPYXUSD'"
    },
    {
      "Currency": "Currency = '$id/JPY'",
      "YieldCurve": "YieldCurve = '$id/JPYOIS'"
    },
    {
      "Currency": "Currency = '$id/HKD'",
      "YieldCurve": "YieldCurve = '$id/HKDDISC'"
    },
    {
      "Currency": "Currency = '$id/CHF'",
      "YieldCurve": "YieldCurve = '$id/CHFOIS'"
    },
    {
      "Currency": "Currency = '$id/HKD'",
      "YieldCurve": "YieldCurve = '$id/HKDDISC'"
    },
    {
      "Currency": "Currency = '$id/CAD'",
      "YieldCurve": "YieldCurve = '$id/CAD-LIBOR'"
    },
    {
      "Currency": "Currency = '$id/CNY'",
      "YieldCurve": "YieldCurve = '$id/CNYCNNDS'"
    }
  ]
}