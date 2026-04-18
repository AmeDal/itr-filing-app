"""
Dynamic prompt templates for different ITR document types.
Designed to extract structured, actionable data via Gemini API.
"""

SYSTEM_PROMPT = (
    "You are a Senior Tax Consultant specializing in Indian Income Tax Returns. "
    "Your goal is to extract structured data from the provided document image(s). "
    "Maintain high precision. If data is missing or ambiguous, do not hallucinate. "
    "Respond with strict JSON following the specified schema."
)

BASE_ITR_PROMPT = (
    "Analyze the provided document. Determine if it matches the expected document type. "
    "Extract all relevant financial details for the Assessment Year specified. "
    "All monetary values should be numbers. Dates should be YYYY-MM-DD. "
    "If the document is NOT what is expected, set is_error to true."
)

PROMPT_TEMPLATES = {
    "FORM_26AS": f"{BASE_ITR_PROMPT} "
                 "Expected Content: Form 26AS (Tax Credit Statement). "
                 "Extract: deductor names, TANs, total amount paid/credited, and total tax deducted (TDS). "
                 "Group by deductor. Identify sections (e.g., Part A, Part B).",
    
    "AIS": f"{BASE_ITR_PROMPT} "
           "Expected Content: Annual Information Statement (AIS). "
           "Extract: Information category (e.g., SFT, TDS, Payment of Taxes), "
           "Description of transaction, expected amounts, and tax-relevant metadata. "
           "Focus on high-value transactions reported by financial institutions.",
    
    "TIS": f"{BASE_ITR_PROMPT} "
           "Expected Content: Taxpayer Information Summary (TIS). "
           "Extract: Information Category, Processed Value, and Taxable Value. "
           "TIS is a summary of AIS—ensure the summary values are accurately captured.",

    "BANK_STATEMENT": f"{BASE_ITR_PROMPT} "
                      "Expected Content: Bank Account Statement. "
                      "Extract: Transaction date, description, deposit amount, withdrawal amount, and balance. "
                      "Flag transactions related to 'Interest', 'Dividend', 'Rent', or 'Salary' specifically. "
                      "Ensure the account number and IFSC are captured if visible.",

    "FORM_16": f"{BASE_ITR_PROMPT} "
               "Expected Content: Form 16 (Salary Certificate). "
               "Extract: Employer Name, Employer TAN, Employee PAN, Salary under Section 17(1), "
               "Allowances under Section 10, Deductions under Chapter VI-A (80C, 80D, etc.), "
               "Total Tax Payable, and Total TDS deducted by employer.",

    "OTHER": f"{BASE_ITR_PROMPT} "
             "Analyze the document and extract any financially relevant data including amounts, dates, and entities. "
             "Classify the document type if possible (e.g., Rent Receipt, Insurance Policy, Donation Receipt)."
}


def get_prompt_for_doc_type(doc_type: str) -> str:
    """Returns the dedicated prompt for a given ITR document type."""
    return PROMPT_TEMPLATES.get(doc_type.upper(), PROMPT_TEMPLATES["OTHER"])
