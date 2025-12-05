import re

# Windows禁止的字符: < > : " / \ | ? *
# 注意：我们不替换路径分隔符 \ 和 / 如果它们看起来像路径的一部分，
# 但在"文件名"输入框中，通常只输入文件名，不包含路径。
# 为了安全起见，如果用户是在输入文件名，这些都是非法的。
INVALID_CHARS = r'[<>:"/\\|?*\x00-\x1F]'
RESERVED_NAMES = r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|$)'

def sanitize_filename(filename):
    if not filename:
        return filename

    # 1. 替换无效字符为下划线
    # 这里简单粗暴一点，把所有非法字符都换掉
    # 如果用户输入的是完整路径（如 C:\Users\...\file.txt），这会破坏路径。
    # 但通常 Save As 对话框的文件名框里只有文件名。
    # 我们做一个简单的判断：如果包含 :\\ 或 ^/，可能是一个路径，我们只处理文件名部分？
    # 现在的需求是"文件名不符合规范"，通常是指文件名本身。
    
    # 简单策略：只替换非法字符
    cleaned = re.sub(INVALID_CHARS, '_', filename)
    
    # 2. 处理保留名称
    if re.match(RESERVED_NAMES, cleaned, re.IGNORECASE):
        cleaned = '_' + cleaned
        
    # 3. 移除末尾的点和空格
    cleaned = cleaned.rstrip('. ')
    
    return cleaned

def has_invalid_chars(filename):
    if not filename:
        return False
    return bool(re.search(INVALID_CHARS, filename) or re.match(RESERVED_NAMES, filename, re.IGNORECASE))
