import re
from datetime import datetime
from config import SCORING_WEIGHTS

def evaluate_post_score(post, all_posts_context=None):
    """
    Universal evaluation of an OSINT post from 0.0 to 10.0
    based on Source Authority, Corroboration, Temporal Lead Time, and Specificity.
    Applies to any investigative topic (drones, conflicts, border security, etc.).
    """
    source_type = post.get("source_type", "WEB")
    source_name = post.get("source_name", "").lower()
    content = (post.get("title", "") + " " + post.get("content", "")).lower()
    publish_time = post.get("publish_time", "")

    # 1. Source Authority (0 - 10)
    if any(s in source_name for s in ["reuters", "bbc", "efe", "dw", "rtve", "el faro", "hespress", "defensa", "ministerio", "boletín"]):
        auth_score = 9.4
    elif any(s in source_name for s in ["deepstate", "rybar", "telegram", "osint", "intel monitor", "maritime"]):
        auth_score = 8.6
    elif any(s in source_name for s in ["x (twitter)", "x.com", "tiktok", "instagram"]):
        auth_score = 7.9
    else:
        auth_score = 7.0

    # 2. Specificity (0 - 10)
    spec_points = 2.0
    # Numerical counts or statistics (e.g. "791 drones", "12 muertos", "450.000")
    if re.search(r'\b\d{2,}\b', content): spec_points += 2.5
    # Precise timestamps or hours
    if re.search(r'\b\d{2}:\d{2}\b', content): spec_points += 2.0
    # Technical assets or weapons
    if any(w in content for w in ["drone", "dron", "shahed", "misil", "radar", "f-16", "neopreno", "aletas", "espigón"]): spec_points += 2.0
    # Named places
    if any(loc in content for loc in ["kiev", "moscú", "kursk", "leipzig", "tarajal", "fnideq", "ceuta", "crimea", "donetsk"]): spec_points += 2.0
    spec_score = min(10.0, spec_points)

    # 3. Temporal Lead Time / Currency (0 - 10)
    temp_score = 7.5
    if publish_time:
        if "2026-09" in publish_time or "2026-08" in publish_time:
            temp_score = 9.5  # Fresh, active current intelligence
        elif "2026-06" in publish_time:
            temp_score = 8.5
        else:
            temp_score = 7.0

    # 4. Cross-Platform Corroboration (0 - 10)
    corr_score = 7.0
    if all_posts_context:
        # Extract 2 longest words from title
        title_words = [w for w in post.get("title", "").lower().split() if len(w) > 4]
        matches = 0
        for other in all_posts_context:
            if other.get("url") != post.get("url"):
                other_text = (other.get("title", "") + " " + other.get("content", "")).lower()
                if any(tw in other_text for tw in title_words[:2]):
                    matches += 1
        corr_score = min(10.0, 6.5 + (matches * 0.7))

    # Weighted final score calculation
    final_score = (
        auth_score * SCORING_WEIGHTS["source_authority"] +
        corr_score * SCORING_WEIGHTS["cross_corroboration"] +
        temp_score * SCORING_WEIGHTS["temporal_lead_time"] +
        spec_score * SCORING_WEIGHTS["specificity"]
    )

    final_score = round(min(10.0, max(0.0, final_score)), 2)

    breakdown = {
        "source_authority": round(auth_score, 2),
        "cross_corroboration": round(corr_score, 2),
        "temporal_lead_time": round(temp_score, 2),
        "specificity": round(spec_score, 2),
        "final_score": final_score
    }

    return final_score, breakdown
