import requests
import re

ORIGINAL_ICS_URL = "https://ics.calendarlabs.com/196/9b1053ae/FIFA_World_Cup.ics"

# 国家→国旗映射
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

# 小组字母对应细框emoji
GROUP_EMOJI = {
    'A':'🅰','B':'🅱','C':'🅲','D':'🅳','E':'🅴','F':'🅵',
    'G':'🅶','H':'🅷','I':'🅸','J':'🅹','K':'🅺','L':'🅻'
}

# RFC5545行折叠
def fold_line(line):
    if len(line.encode('utf-8')) <= 75:
        return line
    result = []
    current = ""
    for char in line:
        if len((current + char).encode('utf-8')) >75:
            result.append(current)
            current = " "+char
        else:
            current += char
    if current:
        result.append(current)
    return '\r\n'.join(result)

def escape_text(text):
    return text.replace('\\','\\\\').replace(',','\\,').replace(';','\\;').replace(':','\\:')

def main():
    resp = requests.get(ORIGINAL_ICS_URL,timeout=30)
    raw = resp.text
    output = [
        fold_line("BEGIN:VCALENDAR"),
        fold_line("VERSION:2.0"),
        fold_line("PRODID:-//Calendar Labs//Calendar 1.0//EN"),
        fold_line("CALSCALE:GREGORIAN"),
        fold_line("METHOD:PUBLISH"),
        fold_line("X-WR-CALNAME:2026 World Cup"),
        fold_line("X-WR-TIMEZONE:UTC")
    ]
    in_event = False
    ev_lines = []
    raw_sum = ""

    for ln in raw.splitlines():
        ln = ln.strip()
        if not ln:continue
        if ln == "BEGIN:VEVENT":
            in_event=True
            ev_lines=[]
            raw_sum=""
        elif ln == "END:VEVENT":
            in_event=False
            # 替换国家为国旗
            for k,v in FLAG_MAPPING.items():
                raw_sum = raw_sum.replace(k,v)
            tag_emoji = ""
            g_find = re.search(r'Group ([A-L])',raw_sum)
            if g_find:
                ch = g_find.group(1)
                tag_emoji = GROUP_EMOJI[ch]
                raw_sum = re.sub(r'Group [A-L]','',raw_sum)
            elif re.search(r'Round of 32',raw_sum):
                tag_emoji = "3️⃣2️⃣"
                raw_sum = re.sub(r'Round of 32','',raw_sum)
            elif re.search(r'Round of 16',raw_sum):
                tag_emoji = "1️⃣6️⃣"
                raw_sum = re.sub(r'Round of 16','',raw_sum)
            elif re.search(r'Quarter-final',raw_sum):
                tag_emoji = "8️⃣"
                raw_sum = re.sub(r'Quarter-final','',raw_sum)
            elif re.search(r'Semi-final',raw_sum):
                tag_emoji = "4️⃣"
                raw_sum = re.sub(r'Semi-final','',raw_sum)
            elif re.search(r'Third Place Playoff',raw_sum):
                tag_emoji = "🥉"
                raw_sum = re.sub(r'Third Place Playoff','',raw_sum)
            elif re.search(r'Final',raw_sum):
                tag_emoji = "🏆"
                raw_sum = re.sub(r'Final','',raw_sum)

            # 清理多余字符
            raw_sum = re.sub(r'Match \d+ - ','',raw_sum)
            raw_sum = re.sub(r'\s+',' ',raw_sum).strip()
            raw_sum = raw_sum.replace('TBD','❓')
            # 优胜者待定统一替换❓ vs ❓
            if re.search(r'runners-up|winner|third place',raw_sum,re.IGNORECASE):
                raw_sum = "❓ vs ❓"

            final_sum = f"{raw_sum} {tag_emoji}".strip()
            # 组装event，丢弃description
            output.append(fold_line("BEGIN:VEVENT"))
            for field in ev_lines:
                if field.startswith("SUMMARY:"):
                    output.append(fold_line(f"SUMMARY:{escape_text(final_sum)}"))
                elif not field.startswith("DESCRIPTION:"):
                    output.append(fold_line(field))
            output.append(fold_line("END:VEVENT"))
        elif in_event:
            if ln.startswith("SUMMARY:"):
                raw_sum = ln[8:]
            ev_lines.append(ln)
    output.append(fold_line("END:VCALENDAR"))
    with open("worldcup_2026_final.ics","w",encoding="utf-8",newline='') as f:
        f.write('\r\n'.join(output))

if __name__ == "__main__":
    main()
