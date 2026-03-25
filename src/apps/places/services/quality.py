from dataclasses import dataclass

from django.utils import timezone

from apps.places.choices import DataIssueSeverity
from apps.places.models import Place, PlaceQualityIssue


@dataclass
class QualityFinding:
    code: str
    severity: str
    message: str
    details: dict


def _within_chile_bounds(place: Place) -> bool:
    if not place.location:
        return True
    return -57 <= place.location.y <= -17 and -77 <= place.location.x <= -66


def build_quality_findings(place: Place) -> list[QualityFinding]:
    findings: list[QualityFinding] = []

    if not place.location:
        findings.append(
            QualityFinding(
                code="missing_location",
                severity=DataIssueSeverity.WARNING,
                message="El lugar no tiene coordenadas geográficas.",
                details={"query": place.geocoding_query},
            )
        )

    if not place.contact_points.exists():
        findings.append(
            QualityFinding(
                code="missing_contact",
                severity=DataIssueSeverity.WARNING,
                message="El lugar no tiene puntos de contacto estructurados.",
                details={},
            )
        )

    if place.is_verified and not place.contact_points.exists():
        findings.append(
            QualityFinding(
                code="verified_without_contact",
                severity=DataIssueSeverity.CRITICAL,
                message="Una ficha verificada debería exponer al menos un contacto.",
                details={},
            )
        )

    if place.is_emergency_service and not place.is_open_24_7:
        findings.append(
            QualityFinding(
                code="emergency_without_24_7_flag",
                severity=DataIssueSeverity.WARNING,
                message="El servicio está marcado como emergencia pero no como 24/7.",
                details={},
            )
        )

    if not _within_chile_bounds(place):
        findings.append(
            QualityFinding(
                code="outside_chile_bounds",
                severity=DataIssueSeverity.CRITICAL,
                message="Las coordenadas no parecen estar dentro del rango esperado para Chile.",
                details={"lat": place.location.y, "lng": place.location.x},
            )
        )

    if not place.summary and not place.description:
        findings.append(
            QualityFinding(
                code="missing_summary",
                severity=DataIssueSeverity.INFO,
                message="La ficha no tiene resumen ni descripción editorial.",
                details={},
            )
        )

    if not place.source_id:
        findings.append(
            QualityFinding(
                code="missing_source",
                severity=DataIssueSeverity.WARNING,
                message="La ficha no tiene una fuente asignada.",
                details={},
            )
        )

    return findings


def _score_for_findings(findings: list[QualityFinding]) -> int:
    score = 100
    weights = {
        DataIssueSeverity.INFO: 5,
        DataIssueSeverity.WARNING: 15,
        DataIssueSeverity.CRITICAL: 40,
    }
    for finding in findings:
        score -= weights[finding.severity]
    return max(score, 0)


def audit_single_place(place: Place) -> list[QualityFinding]:
    findings = build_quality_findings(place)
    current_signatures = {(f.code, f.message) for f in findings}

    open_issues = PlaceQualityIssue.objects.filter(place=place, is_resolved=False)
    for issue in open_issues:
        if (issue.code, issue.message) not in current_signatures:
            issue.mark_resolved()

    for finding in findings:
        PlaceQualityIssue.objects.get_or_create(
            place=place,
            code=finding.code,
            message=finding.message,
            is_resolved=False,
            defaults={
                "severity": finding.severity,
                "details": finding.details,
            },
        )

    place.quality_score = _score_for_findings(findings)
    place.last_quality_check_at = timezone.now()
    place.save(update_fields=["quality_score", "last_quality_check_at", "updated_at"])
    return findings


def audit_places(queryset=None) -> int:
    queryset = queryset or Place.objects.all()
    count = 0
    for place in queryset:
        audit_single_place(place)
        count += 1
    return count
