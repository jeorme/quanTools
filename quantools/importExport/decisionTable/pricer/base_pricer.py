{
  "type": "PricerAssignment",
  "name": "FQP",
  "conditions": [
    {
      "id": "Type",
      "label": "Type"
    },
    {
      "id": "SubType",
      "label": "SubType"
    }
  ],
  "consequences": [
    {
      "id": "Library",
      "label": "Library"
    },
    {
      "id": "PricingModel",
      "label": "Pricing Model"
    },
    {
      "id": "NumericalMethod",
      "label": "Numerical Method"
    },
    {
      "id": "PricingParameters",
      "label": "Pricing Parameters"
    }
  ],
  "rows": [
    {
      "Type": "Type = 'FRA'",
      "Library": "Library = 'FQPIRStandard'",
      "PricingModel": "PricingModel = 'FRA Pricer'",
      "NumericalMethod": "NumericalMethod = 'Deterministic'"
    },
    {
      "Type": "Type = 'IR Swap'",
      "Library": "Library = 'FQPIRStandard'",
      "PricingModel": "PricingModel = 'IRS Pricer'",
      "NumericalMethod": "NumericalMethod = 'Deterministic'",
      "PricingParameters": "PricingParameters = '$id/IRS/itest-convert-before-discount'"
    },
    {
      "Type": "Type = 'Loan/Deposit'",
      "Library": "Library = 'FQPIRStandard'",
      "PricingModel": "PricingModel = 'Loan & Deposit Pricer'",
      "NumericalMethod": "NumericalMethod = 'Deterministic'"
    },
    {
      "Type": "Type in ['Repo', 'Sell Buy Back']",
      "Library": "Library = 'FQPIRStandard'",
      "PricingModel": "PricingModel = 'Securities Financial Pricer'",
      "NumericalMethod": "NumericalMethod = 'Closed Formula'"
    },
    {
      "Type": "Type = 'FX Option'",
      "Library": "Library = 'FQPFXDerivative'",
      "PricingModel": "PricingModel = 'Black Scholes'",
      "NumericalMethod": "NumericalMethod = 'Closed Formula'"
    },
    {
      "Type": "Type in ['FX Swap', 'FX Forward', 'FX Spot']",
      "Library": "Library = 'FQPFXStandard'",
      "PricingModel": "PricingModel = 'Fx Cash Pricer'",
      "NumericalMethod": "NumericalMethod = 'Deterministic'"
    }
  ]
}