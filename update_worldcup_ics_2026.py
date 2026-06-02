import requests
import re

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

def main():
    # 拉取原始ICS
    response = requests.get(ORIGINAL_ICS_URL, timeout=30)
    response.raise_for_status()
    raw = response.text

    # 手动构建新的ICS文件（100%标准格式）
    output = []
    # 先写死标准日历头（绝对不能少）
    output.append("BEGIN:VCALENDAR")
    output.append("VERSION:2.0")
    output.append("PRODID:-//Calendar Labs//Calendar 1.0//EN")
    output.append("CALSCALE:GREGORIAN")
    output.append("METHOD:PUBLISH")
    output.append("X-WR-CALNAME:2026 World Cup")
    output.append("X-WR-TIMEZONE:UTC")

    # 逐行处理原始文件
    in_event = False
    current_event = []
    current_summary = ""

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue

        if line == "BEGIN:VEVENT":
            in_event = True
            current_event = []
            current_summary = ""
        elif line == "END:VEVENT":
            in_event = False
            # 处理当前事件的标题
            for country, flag in FLAG_MAPPING.items():
                current_summary = current_summary.replace(country, flag)

            # 提取阶段/分组
            tag = ""
            g_match = re.search(r'Group ([A-L])', current_summary)
            if g_match:
                tag = f"[{g_match.group(1)}]"
                current_summary = re.sub(r'Group [A-L]', '', current_summary)
            elif re.search(r'Round of 32', current_summary):
                tag = "[R32]"
                current_summary = re.sub(r'Round of 32', '', current_summary)
            elif re.search(r'Round of 16', current_summary):
                tag = "[R16]"
                current_summary = re.sub(r'Round of 16', '', current_summary)
            elif re.search(r'Quarter-final', current_summary):
                tag = "[QF]"
                current_summary = re.sub(r'Quarter-final', '', current_summary)
            elif re.search(r'Semi-final', current_summary):
                tag = "[SF]"
                current_summary = re.sub(r'Semi-final', '', current_summary)
            elif re.search(r'Third Place Playoff', current_summary):
                tag = "[TP]"
                current_summary = re.sub(r'Third Place Playoff', '', current_summary)
            elif re.search(r'Final', current_summary):
                tag = "[F]"
                current_summary = re.sub(r'Final', '', current_summary)

            # 清理多余内容
            current_summary = re.sub(r'Match \d+ - ', '', current_summary)
            current_summary = re.sub(r'\s+', ' ', current_summary).strip()
            current_summary = current_summary.replace('TBD', '❓')

            # 最终标题
            final_summary = f"{current_summary} {tag}".strip()

            # 写入事件（只保留必要字段，删除description）
            output.append("BEGIN:VEVENT")
            for field in current_event:
                if field.startswith("SUMMARY:"):
                    output.append(f"SUMMARY:{final_summary}")
                elif not field.startswith("DESCRIPTION:"):
                    output.append(field)
            output.append("END:VEVENT")

        elif in_event:
            if line.startswith("SUMMARY:"):
                current_summary = line[8:]
            current_event.append(line)

    # 写入日历尾
    output.append("END:VCALENDAR")

    # 保存文件（UTF-8无BOM）
    with open('worldcup_2026_final.ics', 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('\r\n'.join(output))

if __name__ == "__main__":
    main()
