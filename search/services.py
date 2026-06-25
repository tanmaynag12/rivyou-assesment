from django.db.models import Q

from catalog.models import Product

RANK_REASON_CATEGORY = "category_match"
RANK_REASON_TAG = "tag_match"
RANK_REASON_NAME = "product_name_match"
RANK_REASON_DESCRIPTION = "description_match"
RANK_REASON_NAME_AND_DESCRIPTION = "product_name_and_description_match"

TIER_CATEGORY_MIN = 0.70
TIER_TAG_MIN = 0.40
TIER_TEXT_MIN = 0.10


def _coverage_ratio(query: str, target: str) -> float:
    if not target:
        return 0.0
    return min(len(query) / len(target), 1.0)


def _score_category_match(query: str, category: str) -> float:
    query_lower = query.lower()
    category_lower = category.lower()

    if query_lower == category_lower:
        return 1.0

    return round(
        TIER_CATEGORY_MIN + (1.0 - TIER_CATEGORY_MIN) * _coverage_ratio(query_lower, category_lower),
        4,
    )


def _tag_matches(query_lower: str, tags: list[str]) -> bool:
    return any(query_lower in tag for tag in tags)


def _score_tag_match(query: str, tags: list[str]) -> float:
    query_lower = query.lower()
    best_score = 0.0

    for tag in tags:
        tag_lower = tag.lower()
        if query_lower == tag_lower:
            best_score = max(best_score, 0.69)
        elif query_lower in tag_lower:
            score = TIER_TAG_MIN + 0.29 * _coverage_ratio(query_lower, tag_lower)
            best_score = max(best_score, score)

    return round(best_score, 4)


def _score_text_match(query: str, product_name: str, description: str) -> tuple[float, str]:
    query_lower = query.lower()
    name_lower = product_name.lower()
    desc_lower = description.lower()

    name_match = query_lower in name_lower
    desc_match = query_lower in desc_lower

    if name_match and desc_match:
        name_score = 0.30 + 0.09 * _coverage_ratio(query_lower, name_lower)
        desc_score = 0.20 + 0.09 * _coverage_ratio(query_lower, desc_lower)
        return round(max(name_score, desc_score, 0.35), 4), RANK_REASON_NAME_AND_DESCRIPTION

    if name_match:
        score = 0.30 + 0.09 * _coverage_ratio(query_lower, name_lower)
        return round(max(score, TIER_TEXT_MIN), 4), RANK_REASON_NAME

    if desc_match:
        score = 0.15 + 0.14 * _coverage_ratio(query_lower, desc_lower)
        return round(max(score, TIER_TEXT_MIN), 4), RANK_REASON_DESCRIPTION

    return 0.0, ""


def _product_to_result(product: Product, relevance_score: float, rank_reason: str) -> dict:
    return {
        "id": product.id,
        "product_name": product.product_name,
        "description": product.description,
        "category": product.category,
        "tags": product.tags,
        "relevance_score": relevance_score,
        "rank_reason": rank_reason,
    }


def search_products(query: str) -> list[dict]:
    query = query.strip()
    if not query:
        return []

    results: list[dict] = []
    matched_ids: set[int] = set()
    query_lower = query.lower()

    category_products = Product.objects.filter(category__icontains=query).order_by("id")
    for product in category_products:
        matched_ids.add(product.id)
        result = _product_to_result(
            product,
            _score_category_match(query, product.category),
            RANK_REASON_CATEGORY,
        )
        results.append(result)

    tag_candidates = Product.objects.exclude(id__in=matched_ids).order_by("id")
    for product in tag_candidates:
        if not _tag_matches(query_lower, product.tags):
            continue

        matched_ids.add(product.id)
        result = _product_to_result(
            product,
            _score_tag_match(query, product.tags),
            RANK_REASON_TAG,
        )
        results.append(result)

    text_products = (
        Product.objects.exclude(id__in=matched_ids)
        .filter(Q(product_name__icontains=query) | Q(description__icontains=query))
        .order_by("id")
    )
    for product in text_products:
        relevance_score, rank_reason = _score_text_match(
            query,
            product.product_name,
            product.description,
        )
        result = _product_to_result(product, relevance_score, rank_reason)
        results.append(result)

    return results
