'''
Weather condition graphics utility- created for garden dashboard
Provides WMO weather code mappings to SVG graphics and
condition labels sources from Open-Meteo.

Usage:
    from weather_graphics import get_weather_graphic
'''

WEATHER_GRAPHICS = {
    "sunny": {
        "codes": {0, 1},
        "label": "Sunny",
        "svg": """
        <svg viewBox="0 0 80 80" width="80" height="80" xmlns="http://www.w3.org/2000/svg">
            <circle cx="40" cy="40" r="16" fill="#f5c842" opacity="0.95"/>
            <g stroke="#f5c842" stroke-width="3" stroke-linecap="round" opacity="0.8">
                <line x1="40" y1="6"  x2="40" y2="14"/>
                <line x1="40" y1="66" x2="40" y2="74"/>
                <line x1="6"  y1="40" x2="14" y2="40"/>
                <line x1="66" y1="40" x2="74" y2="40"/>
                <line x1="17" y1="17" x2="23" y2="23"/>
                <line x1="57" y1="57" x2="63" y2="63"/>
                <line x1="63" y1="17" x2="57" y2="23"/>
                <line x1="23" y1="57" x2="17" y2="63"/>
            </g>
        </svg>""",
    },
    "partly_cloudy": {
        "codes": {2, 3},
        "label": "Partly Cloudy",
        "svg": """
        <svg viewBox="0 0 80 80" width="80" height="80" xmlns="http://www.w3.org/2000/svg">
            <circle cx="28" cy="38" r="12" fill="#f5c842" opacity="0.9"/>
            <g stroke="#f5c842" stroke-width="2.5" stroke-linecap="round" opacity="0.7">
                <line x1="28" y1="18" x2="28" y2="24"/>
                <line x1="12" y1="38" x2="18" y2="38"/>
                <line x1="15" y1="25" x2="19" y2="29"/>
                <line x1="41" y1="25" x2="37" y2="29"/>
            </g>
            <ellipse cx="50" cy="46" rx="18" ry="11" fill="#d0dcd0" opacity="0.95"/>
            <ellipse cx="38" cy="50" rx="13" ry="9"  fill="#e0e8e0" opacity="0.9"/>
            <ellipse cx="60" cy="50" rx="11" ry="8"  fill="#d8e4d8" opacity="0.85"/>
        </svg>""",
    },
    "cloudy": {
        "codes": {45, 48},
        "label": "Cloudy / Foggy",
        "svg": """
        <svg viewBox="0 0 80 80" width="80" height="80" xmlns="http://www.w3.org/2000/svg">
            <ellipse cx="40" cy="38" rx="22" ry="13" fill="#b0beb0" opacity="0.9"/>
            <ellipse cx="28" cy="44" rx="16" ry="10" fill="#c8d4c8" opacity="0.9"/>
            <ellipse cx="54" cy="44" rx="14" ry="10" fill="#bccabc" opacity="0.85"/>
            <line x1="18" y1="56" x2="62" y2="56" stroke="#9aaa9a" stroke-width="2.5" stroke-linecap="round" opacity="0.5"/>
            <line x1="22" y1="62" x2="58" y2="62" stroke="#9aaa9a" stroke-width="2"   stroke-linecap="round" opacity="0.35"/>
        </svg>""",
    },
    "raining": {
        "codes": {51, 53, 55, 61, 63, 65, 80, 81, 82},
        "label": "Raining",
        "svg": """
        <svg viewBox="0 0 80 80" width="80" height="80" xmlns="http://www.w3.org/2000/svg">
            <ellipse cx="40" cy="32" rx="22" ry="13" fill="#8fa8bf" opacity="0.9"/>
            <ellipse cx="28" cy="38" rx="15" ry="10" fill="#a8c0d4" opacity="0.85"/>
            <ellipse cx="54" cy="38" rx="14" ry="10" fill="#9cb8cc" opacity="0.8"/>
            <g stroke="#6090b8" stroke-width="2.5" stroke-linecap="round" opacity="0.85">
                <line x1="28" y1="52" x2="24" y2="64"/>
                <line x1="40" y1="52" x2="36" y2="64"/>
                <line x1="52" y1="52" x2="48" y2="64"/>
            </g>
        </svg>""",
    },
    "drizzle": {
        "codes": {56, 57, 66, 67},
        "label": "Drizzle",
        "svg": """
        <svg viewBox="0 0 80 80" width="80" height="80" xmlns="http://www.w3.org/2000/svg">
            <ellipse cx="40" cy="32" rx="22" ry="13" fill="#8fa8bf" opacity="0.85"/>
            <ellipse cx="28" cy="38" rx="15" ry="10" fill="#a8c0d4" opacity="0.8"/>
            <ellipse cx="54" cy="38" rx="14" ry="10" fill="#9cb8cc" opacity="0.75"/>
            <g stroke="#6090b8" stroke-width="2" stroke-linecap="round" opacity="0.7">
                <line x1="26" y1="52" x2="24" y2="60"/>
                <line x1="34" y1="54" x2="32" y2="62"/>
                <line x1="42" y1="52" x2="40" y2="60"/>
                <line x1="50" y1="54" x2="48" y2="62"/>
                <line x1="58" y1="52" x2="56" y2="60"/>
            </g>
        </svg>""",
    },
    "snowing": {
        "codes": {71, 73, 75, 77, 85, 86},
        "label": "Snowing",
        "svg": """
        <svg viewBox="0 0 80 80" width="80" height="80" xmlns="http://www.w3.org/2000/svg">
            <ellipse cx="40" cy="30" rx="22" ry="13" fill="#c8d8e8" opacity="0.9"/>
            <ellipse cx="28" cy="36" rx="15" ry="10" fill="#d8e4f0" opacity="0.85"/>
            <ellipse cx="54" cy="36" rx="14" ry="10" fill="#d0dcea" opacity="0.8"/>
            <g fill="#a8c4e0" opacity="0.9">
                <circle cx="28" cy="54" r="3"/>
                <circle cx="40" cy="58" r="3"/>
                <circle cx="52" cy="54" r="3"/>
                <circle cx="34" cy="64" r="2.5"/>
                <circle cx="46" cy="64" r="2.5"/>
            </g>
        </svg>""",
    },
    "thunderstorm": {
        "codes": {95, 96, 99},
        "label": "Thunderstorm",
        "svg": """
        <svg viewBox="0 0 80 80" width="80" height="80" xmlns="http://www.w3.org/2000/svg">
            <ellipse cx="40" cy="28" rx="24" ry="14" fill="#5a6a7a" opacity="0.95"/>
            <ellipse cx="28" cy="36" rx="16" ry="11" fill="#6a7a8a" opacity="0.9"/>
            <ellipse cx="55" cy="35" rx="14" ry="10" fill="#607080" opacity="0.85"/>
            <polygon points="44,42 36,56 42,56 38,70 52,50 44,50" fill="#f5d020" opacity="0.95"/>
        </svg>""",
    },
}

## functions ##
def get_weather_graphic(code:int) -> dict:
    '''
    Return the weather graphic dict matching a WMO weather code.
    Defaults to 'partly_cloudy' if the code is not mapped.

    Parameters
    code : WMO weather interpretation code from Open-Meteo current conditions.

    Returns
        A dict with keys 'label' and 'svg' for the matched condition.
    '''
    for graphic in WEATHER_GRAPHICS.values():
        if code in graphic["codes"]:
            return graphic
    return WEATHER_GRAPHICS["partly_cloudy"]
