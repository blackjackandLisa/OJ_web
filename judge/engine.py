import os
import platform
import shlex
import subprocess
import tempfile
import time
import psutil
import signal
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from .models import JudgeConfig


class JudgeEngine:
    """判题引擎"""
    
    def __init__(self):
        self.judge_dir = getattr(settings, 'JUDGE_DIR', '/tmp/judge')
        self.ensure_judge_dir()
    
    def ensure_judge_dir(self):
        """确保判题目录存在"""
        if not os.path.exists(self.judge_dir):
            os.makedirs(self.judge_dir, exist_ok=True)
    
    def build_command_context(self, file_path: str) -> Dict[str, str]:
        """构建命令格式化上下文"""
        file_dir = os.path.dirname(file_path) or self.judge_dir
        file_name = os.path.basename(file_path)
        file_stem, file_extension = os.path.splitext(file_name)
        file_path_no_ext = os.path.splitext(file_path)[0]
        if platform.system() == 'Windows':
            executable_path = f"{file_path_no_ext}.exe"
            file_path_exe = f"{file_path_no_ext}.exe"
        else:
            executable_path = file_path_no_ext
            file_path_exe = file_path_no_ext

        return {
            'file_path': file_path,
            'file_dir': file_dir,
            'dir': file_dir,
            'file_name': file_name,
            'file_stem': file_stem,
            'class_name': file_stem,
            'file_extension': file_extension,
            'file_path_no_ext': file_path_no_ext,
            'executable': file_path_no_ext,
            'executable_path': executable_path,
            'file_path_exe': file_path_exe,
        }

    def build_command(self, template: str, context: Dict[str, str]) -> List[str]:
        """根据模板和上下文生成命令列表"""
        if not template:
            return []

        command_str = template.format(**context)
        return shlex.split(command_str, posix=platform.system() != 'Windows')

    def get_judge_config(self, language: str) -> Optional[JudgeConfig]:
        """获取编程语言配置"""
        try:
            return JudgeConfig.objects.get(language=language, is_enabled=True)
        except JudgeConfig.DoesNotExist:
            return None
    
    def create_temp_file(self, code: str, language: str) -> str:
        """创建临时文件"""
        config = self.get_judge_config(language)
        if not config:
            raise ValueError(f"不支持的语言: {language}")
        
        # 创建临时文件
        fd, temp_path = tempfile.mkstemp(
            suffix=config.file_extension,
            dir=self.judge_dir,
            text=True
        )
        
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(code)
            return temp_path
        except Exception:
            os.close(fd)
            raise
    
    def compile_code(self, file_path: str, language: str) -> Tuple[bool, str]:
        """编译代码"""
        config = self.get_judge_config(language)
        if not config:
            return False, f"不支持的语言: {language}"
        
        # 某些语言不需要编译
        if language in ['python', 'javascript']:
            return True, ""
        
        try:
            # 构建编译命令
            context = self.build_command_context(file_path)
            compile_cmd = self.build_command(config.compile_command, context)

            if not compile_cmd:
                return False, "缺少编译命令"
            
            # 执行编译
            result = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=False,
                timeout=30,  # 编译超时30秒
                cwd=self.judge_dir
            )
            
            if result.returncode == 0:
                return True, ""
            else:
                stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''
                return False, stderr
                
        except subprocess.TimeoutExpired:
            return False, "编译超时"
        except Exception as e:
            return False, f"编译错误: {str(e)}"
    
    def run_code(self, file_path: str, language: str, input_data: str, 
                 time_limit: int, memory_limit: int) -> Tuple[str, str, int, int, str]:
        """
        运行代码
        返回: (输出, 错误信息, 运行时间, 内存使用, 状态)
        """
        config = self.get_judge_config(language)
        if not config:
            return "", f"不支持的语言: {language}", 0, 0, "system_error"
        
        try:
            # 构建运行命令
            context = self.build_command_context(file_path)
            run_cmd = self.build_command(config.run_command, context)

            if not run_cmd:
                return "", "缺少运行命令", 0, 0, "system_error"
            
            # 记录开始时间
            start_time = time.time()
            
            # 启动进程
            if platform.system() == 'Windows':
                # Windows系统不支持preexec_fn
                process = subprocess.Popen(
                    run_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=False,
                    cwd=self.judge_dir
                )
            else:
                # Unix系统使用preexec_fn创建新的进程组
                process = subprocess.Popen(
                    run_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=False,
                    cwd=self.judge_dir,
                    preexec_fn=os.setsid
                )
            
            # 监控进程
            max_memory = 0
            
            try:
                # 发送输入数据
                input_bytes = (input_data or '').encode('utf-8')
                stdout, stderr = process.communicate(
                    input=input_bytes,
                    timeout=time_limit / 1000.0  # 转换为秒
                )
                
                # 计算运行时间
                end_time = time.time()
                run_time = int((end_time - start_time) * 1000)  # 转换为毫秒
                
                # 检查内存使用
                try:
                    process_info = psutil.Process(process.pid)
                    max_memory = int(process_info.memory_info().rss / 1024)  # 转换为KB
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    max_memory = 0
                
                stdout_text = stdout.decode('utf-8', errors='replace') if stdout else ''
                stderr_text = stderr.decode('utf-8', errors='replace') if stderr else ''

                # 检查是否超时
                if run_time > time_limit:
                    return "", "运行超时", run_time, max_memory, "time_limit_exceeded"
                
                # 检查内存限制
                if max_memory > memory_limit * 1024:  # 转换为KB
                    return "", "内存超限", run_time, max_memory, "memory_limit_exceeded"
                
                # 检查是否有运行时错误
                if process.returncode != 0:
                    return stdout_text, stderr_text, run_time, max_memory, "runtime_error"
                
                return stdout_text, stderr_text, run_time, max_memory, "accepted"
                
            except subprocess.TimeoutExpired:
                # 超时处理
                try:
                    if platform.system() == 'Windows':
                        # Windows系统直接终止进程
                        process.terminate()
                        process.wait(timeout=5)
                    else:
                        # Unix系统终止进程组
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        process.wait(timeout=5)
                except:
                    try:
                        if platform.system() == 'Windows':
                            process.kill()
                        else:
                            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    except:
                        pass
                
                end_time = time.time()
                run_time = int((end_time - start_time) * 1000)
                return "", "运行超时", run_time, max_memory, "time_limit_exceeded"
                
        except Exception as e:
            return "", f"运行错误: {str(e)}", 0, 0, "system_error"
    
    def compare_output(self, expected: str, actual: str) -> bool:
        """比较输出结果"""
        # 标准化输出：去除首尾空白，统一换行符
        expected = expected.strip().replace('\r\n', '\n').replace('\r', '\n')
        actual = actual.strip().replace('\r\n', '\n').replace('\r', '\n')
        
        return expected == actual
    
    def judge_submission(self, submission) -> Dict:
        """判题主函数"""
        from .models import JudgeResult
        
        try:
            # 获取题目和测试用例
            problem = submission.problem
            test_cases = problem.test_cases.filter(is_sample=False)
            
            if not test_cases.exists():
                return {
                    'status': 'system_error',
                    'score': 0,
                    'error_message': '没有找到测试用例',
                    'test_results': []
                }
            
            # 创建临时文件
            temp_file = self.create_temp_file(submission.code, submission.language)
            
            try:
                # 编译代码
                compile_success, compile_error = self.compile_code(temp_file, submission.language)
                if not compile_success:
                    return {
                        'status': 'compile_error',
                        'score': 0,
                        'error_message': compile_error,
                        'test_results': []
                    }
                
                # 运行测试用例
                test_results = []
                total_score = 0
                max_score = test_cases.count() * 10  # 每个测试用例10分
                max_time = 0
                max_memory = 0
                final_status = 'accepted'
                
                for test_case in test_cases:
                    # 运行代码
                    output, error, run_time, memory, status = self.run_code(
                        temp_file,
                        submission.language,
                        test_case.input_data,
                        problem.time_limit,
                        problem.memory_limit
                    )
                    
                    # 更新最大时间和内存
                    max_time = max(max_time, run_time)
                    max_memory = max(max_memory, memory)
                    
                    # 比较输出
                    if status == 'accepted':
                        if self.compare_output(test_case.expected_output, output):
                            test_status = 'accepted'
                            score = 10
                            total_score += score
                        else:
                            test_status = 'wrong_answer'
                            final_status = 'wrong_answer'
                            score = 0
                    else:
                        test_status = status
                        final_status = status
                        score = 0
                    
                    test_results.append({
                        'test_case_id': test_case.id,
                        'input': test_case.input_data,
                        'expected_output': test_case.expected_output,
                        'actual_output': output,
                        'status': test_status,
                        'score': score,
                        'time_used': run_time,
                        'memory_used': memory,
                        'error': error if error else ''
                    })
                
                # 计算最终得分
                final_score = int((total_score / max_score) * 100) if max_score > 0 else 0
                
                return {
                    'status': final_status,
                    'score': final_score,
                    'time_used': max_time,
                    'memory_used': max_memory,
                    'error_message': '',
                    'test_results': test_results
                }
                
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_file)
                    # 清理可能的可执行文件
                    if submission.language == 'cpp':
                        context = self.build_command_context(temp_file)
                        executable_path = context.get('executable_path')
                        if executable_path and os.path.exists(executable_path):
                            os.unlink(executable_path)
                except Exception:
                    pass
                    
        except Exception as e:
            return {
                'status': 'system_error',
                'score': 0,
                'error_message': f"系统错误: {str(e)}",
                'test_results': []
            }
