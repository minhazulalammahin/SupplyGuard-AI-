# SupplyGuard AI: Evaluation & Verification Report

**Evaluation Date:** November 3, 2026  
**Target Scenario:** Aamar Garments Ltd (Fictional) Procurement Benchmark  
**Baseline Dataset:** `purchase-request.csv` (`PR-2026-114`)  
**Supplier Packs:** `supplier-pack-01.pdf` through `supplier-pack-10.pdf`  
**Evaluation Standard:** Company Purchasing Rules (`company-rules.md`)  
**Overall Accuracy:** **10 / 10 packs (100.0%)**

---

## 1. Executive Summary

SupplyGuard AI was evaluated against all 10 supplied supplier quotation packs. The system achieved **100% agreement** with independently verified ground truth without hallucination, false approvals, or decision inversion.

Every rule violation and review trigger is supported by verbatim text citations extracted directly from the original PDF documents via PyMuPDF.

```
Total Evaluated Packs: 10
├── Approved:               2 packs (Pack 01, Pack 02)
├── Needs Person to Check:  3 packs (Pack 04, Pack 07, Pack 09)
└── Rejected:               5 packs (Pack 03, Pack 05, Pack 06, Pack 08, Pack 10)

Accuracy vs Ground Truth:  100.0% (10/10)
Unverified Citations:       0
False Approval Rate:        0.0%
```

---

## 2. Pack-by-Pack Detailed Audit Results

### Pack 01: Padma Textile Mills Ltd
- **Target PR Item:** Item A (`Cotton twill fabric, 280 gsm`) | PR Max Price: 480.00 BDT | PR Qty: 12,000 metres
- **Quoted Terms:** 12,000 metres @ 472.00 BDT ($-1.67\%$ below ceiling)
- **Advance Payment:** 10% ($\le 20\%$ allowable)
- **Delivery:** 24 days ($\le 30$ days rapid fulfillment)
- **Payment Terms:** 45 days after delivery (within 30–60 days window)
- **Penalty Rate:** 1.0% per week of delay ($\ge 0.5\%$)
- **Registration:** TIN `101458013391`, BIN `000170141-0101`
- **VAT:** Itemized separately at 15% (849,600.00 BDT)
- **Expected Decision:** `APPROVE`
- **Actual Decision:** `APPROVE`
- **Exact Citation:** `"10% advance payable with the purchase order. Balance payable within 45 days after delivery and acceptance of goods."`
- **Result:** **MATCH (Pass)**

---

### Pack 02: Jamuna Trims and Accessories
- **Target PR Item:** Item B (`Metal zipper, 18 cm`) | PR Max Price: 38.00 BDT | PR Qty: 20,000 pieces
- **Quoted Terms:** 20,000 pieces @ 36.00 BDT ($-5.26\%$ below ceiling)
- **Advance Payment:** 0% (No advance)
- **Delivery:** 21 days ($\le 30$ days)
- **Payment Terms:** 30 days after delivery (within 30–60 days window)
- **Penalty Rate:** 0.75% per week ($\ge 0.5\%$)
- **Registration:** TIN `102458023391`, BIN `000270241-0101`
- **VAT:** Itemized separately at 15% (108,000.00 BDT)
- **Expected Decision:** `APPROVE`
- **Actual Decision:** `APPROVE`
- **Exact Citation:** `"No advance payment required. Full payment within 30 days of delivery."`
- **Result:** **MATCH (Pass)**

---

### Pack 03: Karnaphuli Yarn Traders
- **Target PR Item:** Item C (`Polyester sewing thread, cone`) | PR Max Price: 210.00 BDT | PR Qty: 800 cones
- **Quoted Terms:** 800 cones @ 229.00 BDT ($+9.05\%$ above ceiling)
- **Violation:** Exceeds maximum unit price by more than 3% ($+9.05\% > 3.0\%$).
- **Triggered Rule:** `R1_PRICE_EXCESS`
- **Expected Decision:** `REJECT`
- **Actual Decision:** `REJECT`
- **Exact Citation:** `"Unit price (BDT): 229.00"`
- **Result:** **MATCH (Pass)**

---

### Pack 04: Surma Packaging Industries
- **Target PR Item:** Item D (`Poly bag, 30 x 40 cm`) | PR Max Price: 6.50 BDT | PR Qty: 50,000 pieces
- **Quoted Terms:** 50,000 pieces @ 6.65 BDT ($+2.31\%$ above ceiling)
- **Finding:** Unit price exceeds maximum, but by no more than 3% ($0 < +2.31\% \le 3.0\%$).
- **Triggered Rule:** `H1_PRICE_MARGINAL_EXCESS`
- **Expected Decision:** `NEEDS_A_PERSON_TO_CHECK`
- **Actual Decision:** `NEEDS_A_PERSON_TO_CHECK`
- **Exact Citation:** `"Unit price (BDT): 6.65"`
- **Result:** **MATCH (Pass)**

---

### Pack 05: Meghna Carton Works
- **Target PR Item:** Item E (`Carton box, 5-ply`) | PR Max Price: 95.00 BDT | PR Qty: 3,000 pieces
- **Quoted Terms:** 3,000 pieces @ 92.00 BDT ($-3.16\%$ compliant)
- **Violation:** Demands 40% advance payment ($40\% > 20\%$).
- **Triggered Rule:** `R2_ADVANCE_PAYMENT`
- **Expected Decision:** `REJECT`
- **Actual Decision:** `REJECT`
- **Exact Citation:** `"1. Payment. 40% advance payable with the purchase order. 40% advance with the purchase order, balance 60% within 30 days of delivery."`
- **Result:** **MATCH (Pass)**

---

### Pack 06: Teesta Fabrics Ltd
- **Target PR Item:** Item A (`Cotton twill fabric, 280 gsm`) | PR Max Price: 480.00 BDT | PR Qty: 12,000 metres
- **Quoted Terms:** 12,000 metres @ 465.00 BDT ($-3.12\%$ compliant)
- **Violation:** Contract contains no late-delivery penalty clause (omitted entirely).
- **Triggered Rule:** `R3_NO_PENALTY_CLAUSE`
- **Expected Decision:** `REJECT`
- **Actual Decision:** `REJECT`
- **Exact Citation:** `[CLAUSE ABSENT FROM TERMS AND CONDITIONS]` (Jumps from Clause 2 "Delivery" to Clause 3 "Validity").
- **Result:** **MATCH (Pass)**

---

### Pack 07: Rupsha Zipper Factory
- **Target PR Item:** Item B (`Metal zipper, 18 cm`) | PR Max Price: 38.00 BDT | PR Qty: 20,000 pieces
- **Quoted Terms:** 16,500 pieces @ 35.00 BDT
- **Finding:** Quoted quantity of 16,500 differs from 20,000 requested by $17.50\%$ ($> 5.0\%$).
- **Triggered Rule:** `H2_QUANTITY_VARIANCE`
- **Expected Decision:** `NEEDS_A_PERSON_TO_CHECK`
- **Actual Decision:** `NEEDS_A_PERSON_TO_CHECK`
- **Exact Citation:** `"Qty: 16,500"`
- **Result:** **MATCH (Pass)**

---

### Pack 08: Bhairab Thread and Co
- **Target PR Item:** Item C (`Polyester sewing thread, cone`) | PR Max Price: 210.00 BDT | PR Qty: 800 cones
- **Quoted Terms:** 800 cones @ 205.00 BDT ($-2.38\%$ compliant)
- **Violation:** Supplier failed to provide TIN or BIN on the quotation.
- **Triggered Rule:** `R4_MISSING_TIN_BIN`
- **Expected Decision:** `REJECT`
- **Actual Decision:** `REJECT`
- **Exact Citation:** `"Supplier registration details available on request."`
- **Result:** **MATCH (Pass)**

---

### Pack 09: Dhaleshwari Poly Pack
- **Target PR Item:** Item D (`Poly bag, 30 x 40 cm`) | PR Max Price: 6.50 BDT | PR Qty: 50,000 pieces
- **Quoted Terms:** 50,000 pieces @ 6.40 BDT
- **Findings:**
  1. **Arithmetic Error:** Table lists Amount BDT `322,000.00`, but $50,000 \times 6.40 = 320,000.00\text{ BDT}$ (a 2,000 BDT calculation error).
  2. **Payment Window:** Clause specifies `"within 30 to 90 days as agreed by both parties"`, exceeding standard 30–60 day payment terms.
- **Triggered Rules:** `H6_ARITHMETIC_ERROR`, `H3_PAYMENT_TERMS_OUTSIDE_WINDOW`
- **Expected Decision:** `NEEDS_A_PERSON_TO_CHECK`
- **Actual Decision:** `NEEDS_A_PERSON_TO_CHECK`
- **Exact Citations:**
  - `"50,000 piece 6.40 322,000.00"`
  - `"1. Payment. 5% advance payable with the purchase order. Payment within 30 to 90 days as agreed by both parties."`
- **Result:** **MATCH (Pass)**

---

### Pack 10: Kushiyara Box Industries
- **Target PR Item:** Item E (`Carton box, 5-ply`) | PR Max Price: 95.00 BDT | PR Qty: 3,000 pieces
- **Quoted Terms:** 3,000 pieces @ 94.00 BDT
- **Violations & Findings:**
  1. **Primary (Reject):** Delivery schedule promised in 60 days ($60 > 45\text{ days}$).
  2. **Secondary (Review):** VAT is not itemized separately at 15% (`"Unit price (BDT, VAT included)"`).
- **Priority Resolution:** Reject takes priority over review.
- **Triggered Rules:** `R5_LATE_DELIVERY` (Primary), `H5_VAT_NOT_SEPARATED` (Secondary)
- **Expected Decision:** `REJECT`
- **Actual Decision:** `REJECT`
- **Exact Citation:** `"2. Delivery. Delivery within 60 days of PO."`
- **Result:** **MATCH (Pass)**

---

## 3. Boundary Condition Test Matrix

| Rule Tested | Boundary Evaluated | Tested Input | Expected Category | Verified Status |
| :--- | :---: | :---: | :---: | :---: |
| Price Ceiling (480.00 max) | $+3.000\%$ | 494.40 BDT | `NEEDS_A_PERSON_TO_CHECK` | **PASS** |
| Price Ceiling (480.00 max) | $+3.002\%$ | 494.45 BDT | `REJECT` | **PASS** |
| Advance Payment | $20.00\%$ | 20.0% | `APPROVE` | **PASS** |
| Advance Payment | $20.10\%$ | 20.1% | `REJECT` | **PASS** |
| Late Delivery Penalty | $0.49\%$/week | 0.49% | `REJECT` | **PASS** |
| Late Delivery Penalty | $0.50\%$/week | 0.50% | `APPROVE` | **PASS** |
| Penalty Clause Presence | Absent | `None` | `REJECT` | **PASS** |
| Supplier Tax ID | Missing TIN | `None` | `REJECT` | **PASS** |
| Supplier Tax ID | Missing BIN | `None` | `REJECT` | **PASS** |
| Delivery Window | 30 days | 30 days | `APPROVE` | **PASS** |
| Delivery Window | 31 days | 31 days | `NEEDS_A_PERSON_TO_CHECK` | **PASS** |
| Delivery Window | 45 days | 45 days | `NEEDS_A_PERSON_TO_CHECK` | **PASS** |
| Delivery Window | 46 days | 46 days | `REJECT` | **PASS** |
| Quantity Variance | $\pm 5.000\%$ | 11,400 (-5.0%) | `APPROVE` | **PASS** |
| Quantity Variance | $\pm 5.008\%$ | 11,399 (-5.01%) | `NEEDS_A_PERSON_TO_CHECK` | **PASS** |
| Payment Schedule | 30–60 days | 30 to 45 days | `APPROVE` | **PASS** |
| Payment Schedule | Outside window | 30 to 90 days | `NEEDS_A_PERSON_TO_CHECK` | **PASS** |
| VAT Itemization | Itemized | 15% line item | `APPROVE` | **PASS** |
| VAT Itemization | Not itemized | VAT included in total | `NEEDS_A_PERSON_TO_CHECK` | **PASS** |
| Arithmetic Consistency | Line error | $100 \times 10 = 1,100$ | `NEEDS_A_PERSON_TO_CHECK` | **PASS** |
| Decision Priority | Reject + Review | 40% adv + Qty diff | `REJECT` (Priority override) | **PASS** |
| Citation Grounding | Unverified quote | Hallucinated text | `NEEDS_A_PERSON_TO_CHECK` | **PASS** |

---

## 4. Conclusion

SupplyGuard AI fulfills all recruitment challenge criteria. The fixed LangGraph pipeline guarantees systematic, traceable audits where AI capabilities are harnessed strictly for information extraction, while business rules remain deterministic, explainable, and fully compliant with enterprise standards.
