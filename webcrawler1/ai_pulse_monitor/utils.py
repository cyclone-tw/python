"""工具函式 - Markdown 清理等共用功能"""

import re


def clean_markdown(content: str) -> str:
    """
    清理 Markdown 內容，移除雜訊

    Args:
        content: 原始 Markdown 內容

    Returns:
        清理後的 Markdown 內容
    """
    if not content:
        return ""

    lines = content.split('\n')
    cleaned_lines = []
    skip_until_next_header = False

    for line in lines:
        # 跳過只有圖片連結的行 (頭像等)
        if re.match(r'^\s*\[!\[.*?\]\(.*?\)\]\(.*?\)\s*$', line):
            continue

        # 跳過列表項中只有圖片連結的行
        if re.match(r'^\s*\*\s*\[!\[.*?\]\(.*?\)\]\(.*?\)\s*$', line):
            continue

        # 跳過 HF 作者頭像連結 (cdn-avatars)
        if 'cdn-avatars.huggingface.co' in line:
            continue

        # 跳過 HF avatars 連結
        if 'huggingface.co/avatars' in line:
            continue

        # 跳過空連結行
        if re.match(r'^\s*\[\s*\]\(.*?\)\s*$', line):
            continue

        # 跳過標題中的空錨點連結
        if re.match(r'^#.*\[\s*\]\(.*?#.*?\)', line):
            line = re.sub(r'\[\s*\]\([^)]+\)\s*', '', line)

        # 跳過只有 Follow 按鈕的行
        if re.match(r'^\[.*?Follow\s*\]\(.*?\)\s*$', line):
            continue

        # 跳過單獨的 "Ad" 行
        if re.match(r'^\s*Ad\s*$', line):
            continue

        # 跳過廣告標記行
        if re.match(r'^\s*DEC_D_Incontent-\d+\s*$', line):
            continue

        # 跳過只有作者頭像的行
        if re.match(r'^\s*\[.*?\'s avatar\]', line):
            continue

        # 跳過 +N 這種顯示更多作者的行
        if re.match(r'^\s*\+\d+\s*$', line):
            continue

        # 跳過只有社群連結的行
        if re.match(r'^\s*\[(Opens discord|Opens LinkedIn|View the LinkedIn)', line):
            continue

        # 跳過作者資訊行 (帶圖片連結的作者名)
        if re.match(r'^\s*\[\s*!\[.*?\]\(.*?\)\s*\]\(.*?/author/', line):
            continue

        # 跳過 LinkedIn Profile 連結行
        if 'View the LinkedIn Profile' in line or 'linkedin.com' in line.lower():
            if re.match(r'^\s*\[.*?\]\(.*?linkedin\.com.*?\)', line):
                continue

        # 跳過訂閱推廣區塊
        if 'Subscribe now' in line or 'the-decoder.com/subscription' in line:
            continue

        # 跳過 THE DECODER subscriber 推廣
        if 'THE DECODER subscriber' in line:
            skip_until_next_header = True
            continue

        # 跳過推廣區塊內容直到下一個標題
        if skip_until_next_header:
            if line.startswith('#'):
                skip_until_next_header = False
            elif 'Source:' in line:
                skip_until_next_header = False
            else:
                continue

        # 跳過 Update on GitHub 連結行
        if re.match(r'^\s*\[Update on GitHub\]', line):
            continue

        # 跳過點讚數行
        if re.match(r'^\s*\[\s*\d+\s*\]\(.*?/login', line):
            continue

        # 清理行內的 "Ask about this article… Search" 等
        line = re.sub(r'Ask about this article[…\.]*\s*Search', '', line)

        # 移除行首的空連結引用
        line = re.sub(r'^\[\s*\]\([^)]+\)\s*', '', line)

        # 移除單獨的作者名連結行
        if re.match(r'^\s*\[[A-Za-z\s]+\]\(.*?/author/.*?\)\s*$', line):
            continue

        cleaned_lines.append(line)

    # 移除連續空行 (超過 2 行的空行縮減為 2 行)
    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip()
