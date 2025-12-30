from datetime import date, datetime

# Ban Seasons
# Format: "START_MONTH-START_DAY", "END_MONTH-END_DAY"
# If end < start, it means it spans across the new year.
BAN_SEASONS = {
    "대구": [("1-16", "2-15")],
    "문치가자미": [("12-1", "1-31")],
    "연어": [("10-1", "11-30")],
    "전어": [("5-1", "7-15")],
    "쥐노래미": [("11-1", "12-31")],
    "참홍어": [("6-1", "7-15")],
    "참조기": [("7-1", "7-31"), ("4-22", "8-10")], # Note: 2nd range is for 'Yujamang', effectively a ban risk period. Simplified to check both or broad? Or just primary. Reference table: 7/1~7/31 (General).
    "갈치": [("7-1", "7-31")],
    "고등어": [("4-1", "6-30")], # "Among 1 month" - ambiguous, usually May-June. Table says "4/1 ~ 6/30 중 1개월". I will assume a warning period or entire range for safety? Let's treat the whole range 4/1-6/30 as potential ban.
    "말쥐치": [("6-1", "7-31")],
    "옥돔": [("7-21", "8-20")],
    "명태": [("1-1", "12-31")], # All year
    "삼치": [("5-1", "5-31")],
    "감성돔": [("5-1", "5-31")],
    "꽃게": [("6-1", "9-30")], # "Among 2 months". Treat as range.
    "대게": [("6-1", "11-30")], # "대게류"
    "붉은대게": [("7-10", "8-25")],
    "대하": [("5-1", "6-30")],
    "새조개": [("6-16", "9-30")],
    "소라": [("6-1", "8-31")],
    "전복": [("9-1", "10-31")], # "전복류"
    "코끼리조개": [("5-1", "6-30")],
    "키조개": [("7-1", "8-31")],
    "가리비": [("3-1", "6-30")],
    "오분자기": [("7-1", "8-31")],
    "넓미역": [("9-1", "11-30")],
    "우뭇가사리": [("11-1", "3-31")],
    "톳": [("10-1", "1-31")],
    "해삼": [("7-1", "7-31")],
    "살오징어": [("4-1", "5-31")],
    "낙지": [("6-1", "6-30")],
    "주꾸미": [("5-11", "8-31")],
    "참문어": [("5-16", "6-30")],
}

# Size Limits (cm)
# If captured size is <= LIMIT, it is forbidden.
SIZE_LIMITS = {
    "문치가자미": 20.0,
    "참가자미": 20.0,
    "감성돔": 25.0,
    "돌돔": 24.0,
    "참돔": 24.0,
    "넙치": 35.0, # 광어
    "농어": 30.0,
    "대구": 35.0,
    "도루묵": 11.0,
    "민어": 33.0,
    "방어": 30.0,
    "볼락": 15.0,
    "붕장어": 35.0,
    "조피볼락": 23.0, # 우럭
    "쥐노래미": 20.0,
    "참홍어": 42.0, # width... handle as length for now?
    "갈치": 18.0, # anal length...
    "고등어": 21.0,
    "참조기": 15.0,
    "말쥐치": 18.0,
    "갯장어": 40.0,
    "미거지": 40.0,
    "용가자미": 20.0,
    "기름가자미": 20.0,
    "청어": 20.0,
    "꽃게": 6.4,
    "대게": 9.0,
    "소라": 5.0, # height
    "마대오분자기": 4.0,
    "전복": 7.0, # "전복류"
    "기수재첩": 1.5,
    "키조개": 18.0,
    "대문어": 600.0, # weight (g)! distinct handling needed? length is passed. If <600g... we have estimatedWeight (kg). 0.6kg.
    "살오징어": 15.0, # mantle length
}

def is_date_in_range(check_date: date, start_str: str, end_str: str) -> bool:
    """Checks if date is within M-D range, handling year wrap."""
    sy, sm, sd = check_date.year, *map(int, start_str.split("-"))
    ey, em, ed = check_date.year, *map(int, end_str.split("-"))
    
    start_date = date(sy, sm, sd)
    end_date = date(ey, em, ed)
    
    if start_date > end_date: # Spans year end (e.g., 12-1 to 1-31)
        # Check if date is after start OR before end
        return check_date >= start_date or check_date <= end_date
    else:
        return start_date <= check_date <= end_date

def check_regulation(fish_name: str, length_cm: float = None, weight_kg: float = None) -> dict:
    """
    Checks if the fish is currently forbidden based on season or size.
    Returns:
        {
            "forbidden": bool,
            "reason": str (or None)
        }
    """
    now = date.today()
    
    # 1. Season Check
    # Handle synonyms or partial matches?
    # For now, strict match or "류" handling (basic contains?)
    # "전복류" -> "전복" in dict.
    
    matched_name = None
    if fish_name in BAN_SEASONS:
        matched_name = fish_name
    else:
        # Fallback: simple contains check
        for key in BAN_SEASONS:
            if key in fish_name:
                matched_name = key
                break
    
    if matched_name:
        ranges = BAN_SEASONS[matched_name]
        for start, end in ranges:
            if is_date_in_range(now, start, end):
                return {"forbidden": True, "reason": f"금지 기간입니다 ({start}~{end})"}

    # 2. Size Check
    if length_cm:
        limit_name = None
        if fish_name in SIZE_LIMITS:
            limit_name = fish_name
        else:
             for key in SIZE_LIMITS:
                if key in fish_name:
                    limit_name = key
                    break
        
        if limit_name:
            limit = SIZE_LIMITS[limit_name]
            
            # Special case for Octopus (weight)
            if limit_name == "대문어":
                if weight_kg and (weight_kg * 1000 < limit):
                     return {"forbidden": True, "reason": f"체중 금지 규격 ({limit}g 이하)"}
            else:
                if length_cm <= limit:
                    return {"forbidden": True, "reason": f"체장 금지 규격 ({limit}cm 이하)"}

    return {"forbidden": False, "reason": None}
