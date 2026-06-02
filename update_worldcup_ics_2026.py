import requests
import re
from icalendar import Calendar, Event

# 原始数据源（CalendarLabs官方，自动更新比分）
ORIGINAL_ICS_URL = "https://ics.calendarlabs.com/196/9b1053ae/FIFA_World_Cup.ics"

# 完整国旗映射表（与原文件球队名100%匹配）
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

# 阶段映射表（按你要求的格式）
STAGE_MAPPING = {
    r'Group ([A-L])': r'[\1]',
    r'Round of 32': '[R32]',
    r'Round of 16': '[R16]',
    r'Quarter-final': '[QF]',
    r'Semi-final': '[SF]',
    r'Third Place Playoff': '[TP]',
    r'Final': '[F]'
}

def process_ics():
    # 拉取最新原始数据
    response = requests.get(ORIGINAL_ICS_URL, timeout=30)
    response.raise_for_status()
    calendar = Calendar.from_ical(response.content)
    
    # 批量处理所有赛事
    for component in calendar.walk():
        if component.name != "VEVENT":
            continue
            
        summary = str(component.get('summary'))
        
        # 替换国家名为国旗
        for country, flag in FLAG_MAPPING.items():
            summary = summary.replace(country, flag)
        
        # 提取并移动阶段标识到末尾
        for pattern, replacement in STAGE_MAPPING.items():
            match = re.search(pattern, summary)
            if match:
                summary = re.sub(pattern, '', summary)
                summary = f"{summary.strip()} {replacement}"
        
        # 清理多余内容
        summary = re.sub(r'Match \d+ - ', '', summary)
        summary = re.sub(r'\s+', ' ', summary)
        summary = summary.replace('TBD', '❓')
        
        component['summary'] = summary
    
    # 保存处理后的文件
    with open('worldcup_2026_final.ics', 'wb') as f:
        f.write(calendar.to_ical())

if __name__ == "__main__":
    process_ics()
