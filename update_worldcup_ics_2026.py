import requests
import re
from icalendar import Calendar, Event

ORIGINAL_ICS_URL = "https://ics.calendarlabs.com/196/9b1053ae/FIFA_World_Cup.ics"

FLAG_MAPPING = {
    'Mexico': '🇲🇽', 'South Africa': '🇿🇦', 'Korean Republic': '🇰🇷', 'Czechia': '🇨🇿',
    'Canada': '🇨🇦', 'Bosnia-Herzegovina': '🇧🇦', 'USA': '🇺🇸', 'Paraguay': '🇵🇾',
    'Qatar': '🇶🇦', 'Switzerland': '🇨🇭', 'Brazil': '🇧🇷', 'Morocco': '🇲🇦',
    'Haiti': '🇭🇹', 'Scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'Australia': '🇦🇺', 'Türkiye': '🇹🇷',
    'Germany': '🇩🇪', 'Curaçao': '🇨🇼', 'Netherlands': '🇳🇱', 'Japan': '🇯🇵',
    "Côte d'Ivoire": '🇨🇮', 'Ecuador': '🇪🇨', 'Sweden': '🇸🇪', 'Tunisia': '🇹🇳',
    'Spain': '🇪🇸', 'Cabo Verde': '🇨🇻', 'Belgium': '🇧🇪', 'Egypt': '🇪🇬',
    'Saudi Arabia': '🇸🇦', 'Uruguay': '🇺🇾', 'IR Iran': '🇮🇷', 'New Zealand': '🇳🇿',
    'France': '🇫🇷', 'Senegal': '🇸🇳', 'Iraq': '🇮🇶', 'Norway': '🇳🇴',
    'Argentina': '🇦🇷', 'Algeria': '🇩🇿', 'Austria': '🇦🇹', 'Jordan': '🇯🇴',
    'Portugal': '🇵🇹', 'Congo DR': '🇨🇩', 'Ghana': '🇬🇭', 'Panama': '🇵🇦',
    'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Croatia': '🇭🇷', 'Uzbekistan': '🇺🇿', 'Colombia': '🇨🇴'
}

# 修复正则：不用\1，改用group(1)拼接，杜绝转义斜杠错乱
def process_ics():
    response = requests.get(ORIGINAL_ICS_URL, timeout=30)
    response.raise_for_status()
    calendar = Calendar.from_ical(response.content)

    for component in calendar.walk():
        if component.name != "VEVENT":
            continue
        summary = str(component.get('summary'))

        # 球队替换国旗
        for country, flag in FLAG_MAPPING.items():
            summary = summary.replace(country, flag)

        tag = ""
        # 提取分组/阶段，不再正则替换拼接
        g_match = re.search(r'Group ([A-L])', summary)
        if g_match:
            tag = f"[{g_match.group(1)}]"
            summary = re.sub(r'Group [A-L]', '', summary)
        elif re.search(r'Round of 32', summary):
            tag = "[R32]"
            summary = re.sub(r'Round of 32', '', summary)
        elif re.search(r'Round of 16', summary):
            tag = "[R16]"
            summary = re.sub(r'Round of 16', '', summary)
        elif re.search(r'Quarter-final', summary):
            tag = "[QF]"
            summary = re.sub(r'Quarter-final', '', summary)
        elif re.search(r'Semi-final', summary):
            tag = "[SF]"
            summary = re.sub(r'Semi-final', '', summary)
        elif re.search(r'Third Place Playoff', summary):
            tag = "[TP]"
            summary = re.sub(r'Third Place Playoff', '', summary)
        elif re.search(r'Final', summary):
            tag = "[F]"
            summary = re.sub(r'Final', '', summary)

        # 删掉Match数字、多余空格、替换待定
        summary = re.sub(r'Match \d+ - ', '', summary)
        summary = re.sub(r'\s+', ' ', summary).strip()
        summary = summary.replace('TBD', '❓')

        # 最终标题：国旗vs国旗 [标识]
        new_sum = f"{summary} {tag}".strip()
        component['summary'] = new_sum

        # ✅ 关键：彻底删除DESCRIPTION字段
        if 'description' in component:
            del component['description']

    with open('worldcup_2026_final.ics', 'wb') as f:
        f.write(calendar.to_ical())

if __name__ == "__main__":
    process_ics()
