import re
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class ParsedProblem:
    """解析后的题目信息"""
    title: str
    description: str
    input_format: str
    output_format: str
    sample_input: str
    sample_output: str
    hint: str
    time_limit: int
    memory_limit: int
    difficulty: str
    test_cases: List[Tuple[str, str]]  # (input, output) pairs


def parse_problem_markdown(markdown_text: str) -> ParsedProblem:
    """
    解析C++题目的Markdown文本，提取题目信息
    
    Args:
        markdown_text: 题目的Markdown文本
        
    Returns:
        ParsedProblem: 解析后的题目信息
        
    Raises:
        ValueError: 当输入文本为空或格式不正确时
    """
    if not markdown_text or not markdown_text.strip():
        raise ValueError("Markdown文本不能为空")
    
    # 验证输入长度
    if len(markdown_text) > 100000:  # 100KB限制
        raise ValueError("Markdown文本过长，请限制在100KB以内")
    # 默认值
    title = ""
    description = ""
    input_format = ""
    output_format = ""
    sample_input = ""
    sample_output = ""
    hint = ""
    time_limit = 1000  # 默认1秒
    memory_limit = 128  # 默认128MB
    difficulty = "简单"
    test_cases = []
    
    # 解析标题 (通常是第一个#标题)
    title_match = re.search(r'^#\s*(.+)$', markdown_text, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    
    # 解析题目描述 (## 题目描述 或 ## 问题描述 后面的内容)
    desc_patterns = [
        r'##\s*(?:题目描述|问题描述)\s*\n(.*?)(?=##|\Z)',
        r'##\s*Description\s*\n(.*?)(?=##|\Z)',
        r'###\s*(?:题目描述|问题描述)\s*\n(.*?)(?=###|##|\Z)'
    ]
    
    for pattern in desc_patterns:
        desc_match = re.search(pattern, markdown_text, re.DOTALL | re.IGNORECASE)
        if desc_match:
            description = desc_match.group(1).strip()
            break
    
    # 解析输入格式
    input_patterns = [
        r'##\s*(?:输入格式|输入)\s*\n(.*?)(?=##|\Z)',
        r'##\s*Input\s*\n(.*?)(?=##|\Z)',
        r'###\s*(?:输入格式|输入)\s*\n(.*?)(?=###|##|\Z)'
    ]
    
    for pattern in input_patterns:
        input_match = re.search(pattern, markdown_text, re.DOTALL | re.IGNORECASE)
        if input_match:
            input_format = input_match.group(1).strip()
            break
    
    # 解析输出格式
    output_patterns = [
        r'##\s*(?:输出格式|输出)\s*\n(.*?)(?=##|\Z)',
        r'##\s*Output\s*\n(.*?)(?=##|\Z)',
        r'###\s*(?:输出格式|输出)\s*\n(.*?)(?=###|##|\Z)'
    ]
    
    for pattern in output_patterns:
        output_match = re.search(pattern, markdown_text, re.DOTALL | re.IGNORECASE)
        if output_match:
            output_format = output_match.group(1).strip()
            break
    
    # 解析样例输入
    sample_input_patterns = [
        r'##\s*(?:样例输入|示例输入)\s*\n```(?:cpp|c\+\+|c|text)?\s*\n(.*?)\n```',
        r'##\s*Sample Input\s*\n```(?:cpp|c\+\+|c|text)?\s*\n(.*?)\n```',
        r'###\s*(?:样例输入|示例输入)\s*\n```(?:cpp|c\+\+|c|text)?\s*\n(.*?)\n```',
        r'###\s*输入\s*#\d+\s*\n```(?:cpp|c\+\+|c|text)?\s*\n(.*?)\n```',
        r'样例输入[：:]\s*\n```(?:cpp|c\+\+|c|text)?\s*\n(.*?)\n```',
        r'输入[：:]\s*\n```(?:cpp|c\+\+|c|text)?\s*\n(.*?)\n```'
    ]
    
    for pattern in sample_input_patterns:
        sample_input_match = re.search(pattern, markdown_text, re.DOTALL | re.IGNORECASE)
        if sample_input_match:
            sample_input = sample_input_match.group(1).strip()
            break
    
    # 解析样例输出
    sample_output_patterns = [
        r'##\s*(?:样例输出|示例输出)\s*\n```(?:cpp|c\+\+|c|text)?\s*\n(.*?)\n```',
        r'##\s*Sample Output\s*\n```(?:cpp|c\+\+|c|text)?\s*\n(.*?)\n```',
        r'###\s*(?:样例输出|示例输出)\s*\n```(?:cpp|c\+\+|c|text)?\s*\n(.*?)\n```',
        r'###\s*输出\s*#\d+\s*\n```(?:cpp|c\+\+|c|text)?\s*\n(.*?)\n```',
        r'样例输出[：:]\s*\n```(?:cpp|c\+\+|c|text)?\s*\n(.*?)\n```',
        r'输出[：:]\s*\n```(?:cpp|c\+\+|c|text)?\s*\n(.*?)\n```'
    ]
    
    for pattern in sample_output_patterns:
        sample_output_match = re.search(pattern, markdown_text, re.DOTALL | re.IGNORECASE)
        if sample_output_match:
            sample_output = sample_output_match.group(1).strip()
            break
    
    # 解析提示
    hint_patterns = [
        r'##\s*(?:提示|说明|注意)\s*\n(.*?)(?=##|\Z)',
        r'##\s*(?:Hint|Note)\s*\n(.*?)(?=##|\Z)',
        r'###\s*(?:提示|说明|注意)\s*\n(.*?)(?=###|##|\Z)'
    ]
    
    for pattern in hint_patterns:
        hint_match = re.search(pattern, markdown_text, re.DOTALL | re.IGNORECASE)
        if hint_match:
            hint = hint_match.group(1).strip()
            break
    
    # 解析时间限制和内存限制
    time_limit_match = re.search(r'(?:时间限制|Time Limit)[：:]\s*(\d+)\s*(?:ms|毫秒|秒)', markdown_text, re.IGNORECASE)
    if time_limit_match:
        time_limit = int(time_limit_match.group(1))
        # 如果是毫秒，转换为毫秒；如果是秒，转换为毫秒
        if '秒' in time_limit_match.group(0) and '毫秒' not in time_limit_match.group(0):
            time_limit *= 1000
    
    memory_limit_match = re.search(r'(?:内存限制|Memory Limit)[：:]\s*(\d+)\s*(?:MB|mb|兆)', markdown_text, re.IGNORECASE)
    if memory_limit_match:
        memory_limit = int(memory_limit_match.group(1))
    
    # 解析难度
    difficulty_patterns = [
        r'(?:难度|Difficulty)[：:]\s*(简单|中等|困难|Easy|Medium|Hard)',
        r'(?:级别|Level)[：:]\s*(简单|中等|困难|Easy|Medium|Hard)'
    ]
    
    for pattern in difficulty_patterns:
        diff_match = re.search(pattern, markdown_text, re.IGNORECASE)
        if diff_match:
            difficulty = diff_match.group(1)
            # 英文转中文
            if difficulty.lower() == 'easy':
                difficulty = '简单'
            elif difficulty.lower() == 'medium':
                difficulty = '中等'
            elif difficulty.lower() == 'hard':
                difficulty = '困难'
            break
    
    # 尝试解析多个测试用例 - 支持 "### 输入 #1" 格式
    multi_test_pattern = r'###\s*(?:输入|输出)\s*#\d+\s*\n```(?:cpp|c\+\+|c|text)?\s*\n(.*?)\n```'
    all_test_blocks = re.findall(multi_test_pattern, markdown_text, re.DOTALL)
    
    # 如果找到多个测试块，尝试配对输入输出
    if len(all_test_blocks) >= 2:
        # 简单策略：奇数位置为输入，偶数位置为输出
        for i in range(0, len(all_test_blocks) - 1, 2):
            input_case = all_test_blocks[i].strip()
            output_case = all_test_blocks[i + 1].strip()
            if input_case and output_case:
                test_cases.append((input_case, output_case))
    
    # 如果上面的方法没有找到，尝试通用的代码块解析
    if not test_cases:
        multi_test_pattern = r'```(?:cpp|c\+\+|c|text)?\s*\n(.*?)\n```'
        all_code_blocks = re.findall(multi_test_pattern, markdown_text, re.DOTALL)
        
        # 如果找到多个代码块，尝试配对输入输出
        if len(all_code_blocks) >= 2:
            # 简单策略：奇数位置为输入，偶数位置为输出
            for i in range(0, len(all_code_blocks) - 1, 2):
                input_case = all_code_blocks[i].strip()
                output_case = all_code_blocks[i + 1].strip()
                if input_case and output_case:
                    test_cases.append((input_case, output_case))
    
    # 如果还是没有找到测试用例，使用样例输入输出
    if not test_cases and sample_input and sample_output:
        test_cases.append((sample_input, sample_output))
    
    # 数据验证和清理
    title = title.strip()[:200] if title else "未命名题目"  # 限制标题长度
    description = description.strip()[:5000] if description else ""  # 限制描述长度
    input_format = input_format.strip()[:2000] if input_format else ""
    output_format = output_format.strip()[:2000] if output_format else ""
    sample_input = sample_input.strip()[:1000] if sample_input else ""
    sample_output = sample_output.strip()[:1000] if sample_output else ""
    hint = hint.strip()[:2000] if hint else ""
    
    # 验证数值范围
    time_limit = max(100, min(time_limit, 10000))  # 100ms - 10s
    memory_limit = max(32, min(memory_limit, 1024))  # 32MB - 1GB
    
    # 验证难度值
    valid_difficulties = ['简单', '中等', '困难', 'easy', 'medium', 'hard']
    if difficulty not in valid_difficulties:
        difficulty = '简单'
    
    # 验证测试用例
    validated_test_cases = []
    for input_case, output_case in test_cases:
        if input_case.strip() and output_case.strip():
            validated_test_cases.append((
                input_case.strip()[:1000],  # 限制输入长度
                output_case.strip()[:1000]  # 限制输出长度
            ))
    
    return ParsedProblem(
        title=title,
        description=description,
        input_format=input_format,
        output_format=output_format,
        sample_input=sample_input,
        sample_output=sample_output,
        hint=hint,
        time_limit=time_limit,
        memory_limit=memory_limit,
        difficulty=difficulty,
        test_cases=validated_test_cases
    )
