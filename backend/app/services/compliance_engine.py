from sqlalchemy.orm import Session
from typing import Dict, Any, List, Tuple, Optional
import logging
import re

from app.models.report import ComplianceReport, ViolationDetail
from app.models.product import Product, ExtractedDeclaration, OCRDeclaration
from app.models.category import ProductCategory, ProductSubcategory
from app.models.rule import ComplianceRule, RuleCategoryMapping
from app.services.scraper.html_downloader import HTMLDownloaderService
from app.services.ai.factory import get_ai_service
from app.services.ocr.engine import OCREngineService

logger = logging.getLogger(__name__)


class ComplianceEngine:
    """
    Upgraded E-Commerce Listing-First Compliance Engine (Section 53 & Critical Debug Architecture).
    Enforces distinct rule evidence sources (ONLINE_MANDATORY, ONLINE_CONDITIONAL,
    PACKAGE_OR_IMAGE_VERIFICATION, PRODUCT_SPECIFIC, NOT_APPLICABLE).
    Differentiates MISSING_FROM_HTML / OCR_REQUIRED from confirmed NON_COMPLIANT failures.
    Calculates multi-state final status: COMPLIANT, REVIEW, NON_COMPLIANT, INSUFFICIENT_EVIDENCE.
    """

    def __init__(self, db: Session):
        self.db = db
        self.ai_service = get_ai_service()
        self.ocr_service = OCREngineService()

    # ------------------------------------------------------------------ #
    #  Step 1 & 2: Scrape HTML and Extract Declarations
    # ------------------------------------------------------------------ #
    def scrape_and_extract(self, product: Product, report: ComplianceReport) -> List[Dict[str, Any]]:
        """Download product page HTML and extract declarations via AI."""
        report.step_reached = 2
        report.reasoning_summary = "Downloading product HTML page..."
        self.db.commit()

        scraped = HTMLDownloaderService.scrape_product_page(product.url)
        product.title = scraped.get("title")
        product.domain = self._extract_domain(product.url)
        product.image_urls = scraped.get("image_urls", [])
        self.db.commit()

        report.step_reached = 3
        report.reasoning_summary = "Extracting mandatory declarations from HTML using AI..."
        self.db.commit()

        html_declarations = self.ai_service.extract_declarations(scraped.get("clean_text", ""))

        for decl in html_declarations:
            self.db.add(ExtractedDeclaration(
                product_id=product.id,
                source="html",
                key_name=decl.get("key_name", "Declaration"),
                raw_value=decl.get("raw_value"),
                normalized_value=decl.get("normalized_value"),
                confidence_score=decl.get("confidence_score", 1.0)
            ))
        self.db.commit()

        return html_declarations

    # ------------------------------------------------------------------ #
    #  Step 3: AI Category & Subcategory Classification + Attributes
    # ------------------------------------------------------------------ #
    def classify_category_and_attributes(
        self, product: Product, report: ComplianceReport, clean_text: str
    ) -> Tuple[ProductCategory, Optional[ProductSubcategory], Dict[str, Any]]:
        """Classify product into a major category, subcategory, and detect conditional attributes."""
        report.step_reached = 4
        report.reasoning_summary = "Classifying category, subcategory, and product attributes..."
        self.db.commit()

        all_categories = self.db.query(ProductCategory).all()
        cat_names = [c.name for c in all_categories]

        combined_text = f"{product.title or ''} {product.url or ''} {clean_text or ''}"
        detected_cat_name = self.ai_service.classify_category(product.title or "", combined_text, cat_names)
        matched_category = self.db.query(ProductCategory).filter(ProductCategory.name == detected_cat_name).first()

        attributes = {}
        if hasattr(self.ai_service, "detect_product_attributes"):
            attributes = self.ai_service.detect_product_attributes(product.title or "", combined_text)

        matched_subcategory = None
        if matched_category:
            report.category_id = matched_category.id
            sub_name = attributes.get("subcategory")
            if sub_name:
                matched_subcategory = self.db.query(ProductSubcategory).filter(
                    ProductSubcategory.category_id == matched_category.id,
                    ProductSubcategory.name == sub_name
                ).first()
                if matched_subcategory:
                    report.subcategory_id = matched_subcategory.id

        report.detected_attributes = attributes
        self.db.commit()

        return matched_category, matched_subcategory, attributes

    # ------------------------------------------------------------------ #
    #  Step 4: Retrieve Category-Specific Rules from PostgreSQL
    # ------------------------------------------------------------------ #
    def retrieve_applicable_rules(self, category: ProductCategory) -> List[ComplianceRule]:
        """Fetch all rules mapped to the detected product category."""
        applicable_rules: List[ComplianceRule] = []
        if category:
            mappings = self.db.query(RuleCategoryMapping).filter(
                RuleCategoryMapping.category_id == category.id
            ).all()
            applicable_rules = [m.rule for m in mappings if m.rule]

        if not applicable_rules:
            applicable_rules = self.db.query(ComplianceRule).filter(
                ComplianceRule.rule_code.like("LM-CORE-%")
            ).all()

        return applicable_rules

    # ------------------------------------------------------------------ #
    #  Rule Applicability Evaluator (Dynamic Condition Matching)
    # ------------------------------------------------------------------ #
    @staticmethod
    def is_rule_applicable(
        rule: ComplianceRule, attributes: Dict[str, Any], subcategory: Optional[ProductSubcategory]
    ) -> bool:
        """
        Evaluate dynamic condition matching for CONDITIONAL rules (Section 53B).
        Returns True if applicable, False if NOT_APPLICABLE.
        """
        if rule.applicability_type != "CONDITIONAL" or not rule.applicability_condition_json:
            return True

        cond = rule.applicability_condition_json
        attr_name = cond.get("attribute")
        op = cond.get("operator", "equals")
        expected_val = cond.get("value")

        actual_val = attributes.get(attr_name)
        if attr_name == "subcategory" and subcategory:
            actual_val = subcategory.name

        if op == "equals":
            return actual_val == expected_val
        elif op == "in" and isinstance(expected_val, list):
            return actual_val in expected_val

        return True

    # ------------------------------------------------------------------ #
    #  Legacy Static Helper for Test Compatibility
    # ------------------------------------------------------------------ #
    @staticmethod
    def _classify_violation(
        status: str, actual_found: str, confidence: float, enforcement_level: str
    ) -> Tuple[str, str]:
        """
        Classify violation as MISSING, INCORRECT, or AMBIGUOUS with severity assignment.
        Returns (violation_type, severity).
        """
        if status in ["PASSED", "COMPLIANT"] and confidence >= 0.5:
            return "PASSED", "none"

        actual_lower = actual_found.lower().strip() if actual_found else ""

        if not actual_lower or actual_lower in ["not found", "n/a", "none", ""]:
            severity = "critical" if enforcement_level == "strict" else "warning"
            return "MISSING", severity

        if confidence < 0.5:
            severity = "warning"
            return "AMBIGUOUS", severity

        if status not in ["PASSED", "COMPLIANT", "NOT_APPLICABLE"]:
            severity = "critical" if enforcement_level == "strict" else "moderate"
            return "INCORRECT", severity

        return "PASSED", "none"

    # ------------------------------------------------------------------ #
    #  Step 5 & 6: Compare Declarations vs Rules with Section 53 Logic
    # ------------------------------------------------------------------ #
    def evaluate_declarations(
        self,
        report: ComplianceReport,
        applicable_rules: List[ComplianceRule],
        declarations: List[Dict[str, Any]],
        attributes: Dict[str, Any],
        subcategory: Optional[ProductSubcategory],
        step_label: str = "HTML"
    ) -> Tuple[int, int, int]:
        """
        Compare extracted declarations against each rule.
        Enforces distinct evidence-source handling:
        - ONLINE_MANDATORY
        - ONLINE_CONDITIONAL
        - PACKAGE_OR_IMAGE_VERIFICATION
        - PRODUCT_SPECIFIC
        - NOT_APPLICABLE
        """
        report.step_reached = 5 if step_label == "HTML" else 9
        report.reasoning_summary = f"Evaluating {step_label} declarations against Legal Metrology rules..."
        report.html_checked = True
        self.db.commit()

        passed_count = 0
        failed_count = 0
        not_applicable_count = 0

        for rule in applicable_rules:
            # 1. Check Dynamic Applicability Condition (Section 53B / Section 9 Fix)
            if not self.is_rule_applicable(rule, attributes, subcategory):
                not_applicable_count += 1
                self.db.add(ViolationDetail(
                    report_id=report.id,
                    rule_id=rule.id,
                    status="NOT_APPLICABLE",
                    evidence_status="NOT_APPLICABLE",
                    evidence_source=rule.evidence_source,
                    field_name=rule.declaration_name,
                    expected_rule=rule.mandatory_fields,
                    actual_found="Not Applicable for product attributes",
                    confidence=1.0,
                    ai_reasoning=f"[NOT_APPLICABLE] Rule condition ({rule.applicability_condition_json}) did not match product."
                ))
                continue

            # 2. Evaluate Declaration Compliance via AI/Normalization Provider
            eval_result = self.ai_service.evaluate_rule_compliance(
                rule.declaration_name,
                rule.mandatory_fields,
                declarations
            )

            raw_status = eval_result.get("status", "FAILED")
            actual_found = eval_result.get("actual_found", "Not Found")
            confidence = eval_result.get("confidence", 0.0)

            # Determine source of declaration if found
            decl_source = "HTML"
            if raw_status == "PASSED":
                for d in declarations:
                    if d.get("source") == "ocr":
                        decl_source = "IMAGE_OCR"
                        break

            # 3. Rule Evidence Source & Classification Logic
            rule_type = getattr(rule, "rule_type", "ONLINE_MANDATORY")
            is_package_verifiable = (
                rule_type == "PACKAGE_OR_IMAGE_VERIFICATION"
                or rule.evidence_source in ["PACKAGE_ONLY", "IMAGE_OCR", "HTML_OR_IMAGE", "PACKAGE_OR_IMAGE"]
            )

            if raw_status == "PASSED":
                passed_count += 1
                final_status = "PASSED"
                evidence_status = "FOUND_BY_OCR" if decl_source == "IMAGE_OCR" else "FOUND"
            else:
                if is_package_verifiable and step_label == "HTML":
                    # Section 53C & Critical Debug: HTML missing -> PACKAGE/IMAGE VERIFICATION REQUIRED (REVIEW status)
                    final_status = "REVIEW"
                    evidence_status = "MISSING_FROM_HTML"
                    failed_count += 1
                else:
                    failed_count += 1
                    final_status = "FAILED"
                    evidence_status = "INSUFFICIENT_EVIDENCE" if confidence < 0.5 else "INVALID"

            reasoning = eval_result.get("ai_reasoning", "")
            if final_status not in ["PASSED", "NOT_APPLICABLE"]:
                reasoning = f"[{rule_type} | {evidence_status}] {reasoning}"

            self.db.add(ViolationDetail(
                report_id=report.id,
                rule_id=rule.id,
                status=final_status,
                evidence_status=evidence_status,
                evidence_source=rule.evidence_source,
                field_name=rule.declaration_name,
                expected_rule=rule.mandatory_fields,
                actual_found=actual_found,
                confidence=confidence,
                ai_reasoning=reasoning
            ))

        self.db.commit()
        return passed_count, failed_count, not_applicable_count

    # ------------------------------------------------------------------ #
    #  Step 7 & 8: OCR Workflow (Triggered ONLY on Applicable Package Rules)
    # ------------------------------------------------------------------ #
    def run_ocr_workflow(self, product: Product, report: ComplianceReport) -> List[Dict[str, Any]]:
        """Download product images, preprocess with OpenCV, extract OCR text, and return declarations."""
        report.step_reached = 8
        report.reasoning_summary = "Triggering OCR packaging analysis on product images..."
        report.ocr_checked = True
        self.db.commit()

        ocr_declarations = []
        for img_url in (product.image_urls or [])[:3]:
            ocr_res = self.ocr_service.process_image_url(img_url)
            self.db.add(OCRDeclaration(
                product_id=product.id,
                image_url=img_url,
                detected_text=ocr_res.get("detected_text"),
                corrected_text=ocr_res.get("detected_text")
            ))

            for d in ocr_res.get("declarations", []):
                d["source"] = "ocr"
                ocr_declarations.append(d)
                self.db.add(ExtractedDeclaration(
                    product_id=product.id,
                    source="ocr",
                    key_name=d.get("key_name", "OCR Declaration"),
                    raw_value=d.get("raw_value"),
                    normalized_value=d.get("normalized_value"),
                    confidence_score=d.get("confidence_score", 0.85)
                ))
        self.db.commit()
        return ocr_declarations

    # ------------------------------------------------------------------ #
    #  Step 9 & 10: Status & Compliance Score Computation (Section 12 & 13)
    # ------------------------------------------------------------------ #
    def compute_score_and_explain(
        self,
        report: ComplianceReport,
        product: Product,
        category: ProductCategory,
        applicable_rules: List[ComplianceRule],
        passed_count: int,
        failed_count: int,
        not_applicable_count: int
    ):
        """
        Compute final compliance score:
        Score = (Passed Applicable Weight / Total Applicable Weight) * 100.0
        Excludes NOT_APPLICABLE from denominator.
        Determines multi-state final status: COMPLIANT, REVIEW, NON_COMPLIANT, INSUFFICIENT_EVIDENCE.
        """
        report.step_reached = 10

        all_violations = self.db.query(ViolationDetail).filter(ViolationDetail.report_id == report.id).all()
        violation_map = {v.rule_id: v for v in all_violations}

        total_applicable_weight = 0.0
        passed_applicable_weight = 0.0

        for rule in applicable_rules:
            v = violation_map.get(rule.id)
            if v and v.status == "NOT_APPLICABLE":
                continue

            weight = 2.0 if rule.enforcement_level == "strict" else 1.0
            total_applicable_weight += weight
            if v and v.status == "PASSED":
                passed_applicable_weight += weight

        calculated_score = (passed_applicable_weight / total_applicable_weight * 100.0) if total_applicable_weight > 0 else 100.0
        report.overall_score = round(min(100.0, max(0.0, calculated_score)), 2)

        # Count Genuine Online Failures vs Package Verification Pending (Section 53E & 53G & Debug Section 13)
        online_strict_failed = 0
        package_review_count = 0

        for rule in applicable_rules:
            v = violation_map.get(rule.id)
            if not v or v.status in ["PASSED", "NOT_APPLICABLE"]:
                continue

            rule_type = getattr(rule, "rule_type", "ONLINE_MANDATORY")

            if v.status == "REVIEW" or rule_type in ["PACKAGE_OR_IMAGE_VERIFICATION"] or rule.evidence_source in ["PACKAGE_ONLY", "IMAGE_OCR", "HTML_OR_IMAGE", "PACKAGE_OR_IMAGE"]:
                package_review_count += 1
            elif rule.enforcement_level == "strict":
                online_strict_failed += 1

        # Multi-State Final Status Determination
        if online_strict_failed == 0 and package_review_count == 0 and report.overall_score == 100.0:
            report.overall_status = "COMPLIANT"
        elif online_strict_failed > 0:
            report.overall_status = "NON_COMPLIANT"
        elif package_review_count > 0:
            report.overall_status = "REVIEW"
        elif report.overall_score >= 85.0:
            report.overall_status = "REVIEW"
        else:
            report.overall_status = "NON_COMPLIANT"

        passed_names = [v.field_name for v in all_violations if v.status == "PASSED"]
        failed_names = [v.field_name for v in all_violations if v.status not in ["PASSED", "NOT_APPLICABLE", "REVIEW"]]
        review_names = [v.field_name for v in all_violations if v.status == "REVIEW"]
        na_names = [v.field_name for v in all_violations if v.status == "NOT_APPLICABLE"]

        category_name = category.name if category else "Packaged Commodities"
        report.reasoning_summary = self.ai_service.generate_explanation(
            product_title=product.title or "E-Commerce Product",
            category=category_name,
            passed_rules=passed_names,
            failed_rules=failed_names,
            review_rules=review_names,
            not_applicable_rules=na_names
        )
        self.db.commit()

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain name from URL."""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except Exception:
            return ""


# ====================================================================== #
#  Public Entry Point (backward compatible)
# ====================================================================== #
def run_full_compliance_workflow(report_id: int, db: Session):
    """
    Public entry point for the Legal Metrology Compliance Pipeline.
    Called by FastAPI endpoints and Celery background tasks.
    """
    report = db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
    if not report:
        logger.error(f"Report {report_id} not found")
        return

    product = report.product
    engine = ComplianceEngine(db)

    try:
        # Step 0: Live Product URL Discovery & Verification (Section 1-12)
        from app.services.discovery.url_verifier import LiveURLVerifierService, VerificationStatus
        ver_res = LiveURLVerifierService.verify_product_url(product.url)
        if not ver_res.get("is_verified", False):
            report.overall_status = "FAILED"
            report.overall_score = 0.0
            report.step_reached = 1
            status_code = ver_res.get("http_status", 0)
            ver_status = ver_res.get("verification_status", VerificationStatus.DEAD_URL)
            err_msg = ver_res.get("error_reason", "Live URL Verification Failed")
            report.reasoning_summary = f"[{ver_status}] HTTP {status_code}: {err_msg}. URL is inaccessible, blocked, or not a valid product page."
            db.commit()
            logger.warning(f"Compliance pipeline halted for report #{report.id}: {report.reasoning_summary}")
            return

        # Store canonical URL from live verification redirect
        if ver_res.get("canonical_url") and ver_res["canonical_url"] != product.url:
            product.url = ver_res["canonical_url"]
            db.commit()

        # Steps 1-2: Scrape HTML and extract declarations
        html_declarations = engine.scrape_and_extract(product, report)

        # Step 3: Classify category, subcategory, and product attributes
        scraped = HTMLDownloaderService.scrape_product_page(product.url)
        matched_category, matched_subcategory, attributes = engine.classify_category_and_attributes(
            product, report, scraped.get("clean_text", "")
        )

        # Step 4: Retrieve category-specific rules from PostgreSQL
        applicable_rules = engine.retrieve_applicable_rules(matched_category)

        # Steps 5-6: Compare HTML declarations against rules
        passed_count, failed_count, not_applicable_count = engine.evaluate_declarations(
            report, applicable_rules, html_declarations, attributes, matched_subcategory, step_label="HTML"
        )

        # Check if OCR is needed (Section 53C Workflow: HTML NOT FOUND -> PACKAGE/IMAGE VERIFICATION REQUIRED -> OCR)
        rules_requiring_ocr = [
            r for r in applicable_rules
            if engine.is_rule_applicable(r, attributes, matched_subcategory)
            and (getattr(r, "rule_type", "") == "PACKAGE_OR_IMAGE_VERIFICATION" or r.evidence_source in ["PACKAGE_ONLY", "IMAGE_OCR", "HTML_OR_IMAGE", "PACKAGE_OR_IMAGE"])
        ]

        if failed_count > 0 and product.image_urls and rules_requiring_ocr:
            ocr_declarations = engine.run_ocr_workflow(product, report)
            combined_declarations = html_declarations + ocr_declarations

            # Clear existing violations for re-evaluation
            db.query(ViolationDetail).filter(ViolationDetail.report_id == report.id).delete()
            db.commit()

            # Step 9: Re-evaluate with combined HTML + OCR declarations
            passed_count, failed_count, not_applicable_count = engine.evaluate_declarations(
                report, applicable_rules, combined_declarations, attributes, matched_subcategory, step_label="HTML+OCR"
            )

        # Step 10: Compute score and generate Section 53 multi-state status summary
        engine.compute_score_and_explain(
            report, product, matched_category, applicable_rules, passed_count, failed_count, not_applicable_count
        )

        logger.info(f"Compliance pipeline completed for report #{report.id}: {report.overall_status} ({report.overall_score}%)")

    except Exception as e:
        report.overall_status = "FAILED"
        report.reasoning_summary = f"Compliance pipeline encountered an error: {str(e)}"
        report.step_reached = report.step_reached or 1
        db.commit()
        logger.error(f"Compliance pipeline failed for report #{report.id}: {e}", exc_info=True)
