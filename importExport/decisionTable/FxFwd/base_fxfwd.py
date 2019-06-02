{
  "type": "FxForward",
  "name": "FQP",
  "conditions": [
    {
      "id": "Currency_1",
      "label": "Currency_1"
    },
    {
      "id": "Currency_2",
      "label": "Currency_2"
    },
    {
      "id": "trade:collateral_ccy",
      "label": "trade:collateral_ccy"
    }
  ],
  "consequences": [
    {
      "id": "FX_Forward_IR_Curve_1",
      "label": "FX_Forward_IR_Curve_1"
    },
    {
      "id": "FX_Forward_IR_Curve_2",
      "label": "FX_Forward_IR_Curve_2"
    }
  ],
  "rows": [
    {
      "Currency_1": "Currency_1='$id/EUR'",
      "FX_Forward_IR_Curve_1": "FX_Forward_IR_Curve_1='$id/EUROIS'"
    },
    {
      "Currency_1": "Currency_1='$id/USD'",
      "FX_Forward_IR_Curve_1": "FX_Forward_IR_Curve_1='$id/USDOIS'"
    },
    {
      "Currency_1": "Currency_1='$id/JPY'",
      "FX_Forward_IR_Curve_1": "FX_Forward_IR_Curve_1='$id/JPYOIS'"
    },
    {
      "Currency_1": "Currency_1='$id/GBP'",
      "FX_Forward_IR_Curve_1": "FX_Forward_IR_Curve_1='$id/GBPOIS'"
    },
    {
      "Currency_1": "Currency_1='$id/MXN'",
      "FX_Forward_IR_Curve_1": "FX_Forward_IR_Curve_1='$id/MXNOIS'"
    },
    {
      "Currency_1": "Currency_1='$id/CLP'",
      "FX_Forward_IR_Curve_1": "FX_Forward_IR_Curve_1='$id/CLPGOV'"
    },
    {
      "Currency_1": "Currency_1='$id/UDI'",
      "FX_Forward_IR_Curve_1": "FX_Forward_IR_Curve_1='$id/UDISBMT'"
    },
    {
      "Currency_1": "Currency_1='$id/HKD'",
      "FX_Forward_IR_Curve_1": "FX_Forward_IR_Curve_1='$id/HKDDISC'"
    },
    {
      "Currency_1": "Currency_1='$id/CHF'",
      "FX_Forward_IR_Curve_1": "FX_Forward_IR_Curve_1='$id/CHFOIS'"
    },
    {
      "Currency_1": "Currency_1='$id/CNY'",
      "FX_Forward_IR_Curve_1": "FX_Forward_IR_Curve_1='$id/CNYCNNDS'"
    },
    {
      "Currency_1": "Currency_1='$id/CAD'",
      "FX_Forward_IR_Curve_1": "FX_Forward_IR_Curve_1='$id/CAD-LIBOR'"
    }
  ]
}