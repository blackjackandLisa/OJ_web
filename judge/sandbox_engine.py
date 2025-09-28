"""
沙箱判题引擎 - 使用进程隔离和资源限制
"""
import os
import psutil
import signal
import subprocess
import tempfile
import time
import resource
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from .models import JudgeConfig


class SandboxEngine:
    """沙箱判题引擎 - 提供进程级别的安全隔离"""
    
    def __init__(self):
        self.judge_dir = getattr(settings, 'JUDGE_DIR', '/tmp/judge')
        self.sandbox_dir = os.path.join(self.judge_dir, 'sandbox')
        self.ensure_directories()
        
    def ensure_directories(self):
        """确保必要目录存在"""
        os.makedirs(self.judge_dir, exist_ok=True)
        os.makedirs(self.sandbox_dir, exist_ok=True)
        
    def get_judge_config(self, language: str) -> Optional[JudgeConfig]:
        """获取编程语言配置"""
        try:
            return JudgeConfig.objects.get(language=language, is_enabled=True)
        except JudgeConfig.DoesNotExist:
            return None
    
    def create_sandbox_environment(self, code: str, language: str) -> Dict[str, str]:
        """创建沙箱环境"""
        config = self.get_judge_config(language)
        if not config:
            raise ValueError(f"不支持的语言: {language}")
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(dir=self.sandbox_dir)
        
        # 写入用户代码
        code_file = os.path.join(temp_dir, f"solution{config.file_extension}")
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return {
            'temp_dir': temp_dir,
            'code_file': code_file
        }
    
    def set_resource_limits(self, time_limit: int, memory_limit: int):
        """设置资源限制"""
        # 设置CPU时间限制（秒）
        resource.setrlimit(resource.RLIMIT_CPU, (time_limit // 1000, time_limit // 1000))
        
        # 设置内存限制（字节）
        memory_bytes = memory_limit * 1024 * 1024  # 转换为字节
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        
        # 设置文件大小限制
        resource.setrlimit(resource.RLIMIT_FSIZE, (100 * 1024 * 1024, 100 * 1024 * 1024))  # 100MB
        
        # 设置进程数限制
        resource.setrlimit(resource.RLIMIT_NPROC, (50, 50))
        
        # 设置文件描述符限制
        resource.setrlimit(resource.RLIMIT_NOFILE, (100, 100))
    
    def run_secure_process(self, command: List[str], input_data: str, 
                          time_limit: int, memory_limit: int) -> Dict:
        """运行安全的进程"""
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 启动进程
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=self.set_resource_limits(time_limit, memory_limit),
                cwd=self.sandbox_dir
            )
            
            # 监控进程
            max_memory = 0
            process_info = None
            
            try:
                # 发送输入数据
                stdout, stderr = process.communicate(
                    input=input_data or '',
                    timeout=time_limit / 1000.0
                )
                
                # 计算运行时间
                end_time = time.time()
                run_time = int((end_time - start_time) * 1000)
                
                # 获取内存使用情况
                try:
                    process_info = psutil.Process(process.pid)
                    max_memory = int(process_info.memory_info().rss / 1024)  # KB
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    max_memory = 0
                
                # 检查状态
                if process.returncode == 0:
                    status = 'accepted'
                elif process.returncode == 124:  # timeout
                    status = 'time_limit_exceeded'
                elif process.returncode == 137:  # killed
                    status = 'memory_limit_exceeded'
                else:
                    status = 'runtime_error'
                
                return {
                    'success': True,
                    'output': stdout,
                    'error': stderr,
                    'time_used': run_time,
                    'memory_used': max_memory,
                    'status': status
                }
                
            except subprocess.TimeoutExpired:
                # 超时处理
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    try:
                        process.kill()
                    except:
                        pass
                
                end_time = time.time()
                run_time = int((end_time - start_time) * 1000)
                
                return {
                    'success': True,
                    'output': '',
                    'error': '运行超时',
                    'time_used': run_time,
                    'memory_used': max_memory,
                    'status': 'time_limit_exceeded'
                }
                
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': f'进程执行错误: {str(e)}',
                'time_used': 0,
                'memory_used': 0,
                'status': 'system_error'
            }
    
    def compile_code(self, code_file: str, language: str) -> Tuple[bool, str]:
        """编译代码"""
        config = self.get_judge_config(language)
        if not config:
            return False, f"不支持的语言: {language}"
        
        # 某些语言不需要编译
        if language in ['python', 'javascript']:
            return True, ""
        
        try:
            # 构建编译命令
            compile_cmd = config.compile_command.format(
                file_path=code_file,
                file_dir=os.path.dirname(code_file),
                file_name=os.path.basename(code_file),
                file_stem=os.path.splitext(os.path.basename(code_file))[0]
            ).split()
            
            # 执行编译
            result = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.path.dirname(code_file)
            )
            
            if result.returncode == 0:
                return True, ""
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "编译超时"
        except Exception as e:
            return False, f"编译错误: {str(e)}"
    
    def run_code(self, code_file: str, language: str, input_data: str,
                time_limit: int, memory_limit: int) -> Dict:
        """运行代码"""
        config = self.get_judge_config(language)
        if not config:
            return {
                'success': False,
                'output': '',
                'error': f"不支持的语言: {language}",
                'time_used': 0,
                'memory_used': 0,
                'status': 'system_error'
            }
        
        try:
            # 编译代码
            compile_success, compile_error = self.compile_code(code_file, language)
            if not compile_success:
                return {
                    'success': False,
                    'output': '',
                    'error': compile_error,
                    'time_used': 0,
                    'memory_used': 0,
                    'status': 'compile_error'
                }
            
            # 构建运行命令
            run_cmd = config.run_command.format(
                file_path=code_file,
                file_dir=os.path.dirname(code_file),
                file_name=os.path.basename(code_file),
                file_stem=os.path.splitext(os.path.basename(code_file))[0]
            ).split()
            
            # 运行代码
            return self.run_secure_process(run_cmd, input_data, time_limit, memory_limit)
            
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': f'运行错误: {str(e)}',
                'time_used': 0,
                'memory_used': 0,
                'status': 'system_error'
            }
    
    def judge_submission(self, submission) -> Dict:
        """判题主函数"""
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
            
            # 创建沙箱环境
            sandbox = self.create_sandbox_environment(submission.code, submission.language)
            
            try:
                # 运行测试用例
                test_results = []
                total_score = 0
                max_score = test_cases.count() * 10
                max_time = 0
                max_memory = 0
                final_status = 'accepted'
                
                for test_case in test_cases:
                    # 运行代码
                    result = self.run_code(
                        sandbox['code_file'],
                        submission.language,
                        test_case.input_data,
                        problem.time_limit,
                        problem.memory_limit
                    )
                    
                    # 更新最大时间和内存
                    max_time = max(max_time, result['time_used'])
                    max_memory = max(max_memory, result['memory_used'])
                    
                    # 比较输出
                    if result['status'] == 'accepted':
                        if self.compare_output(test_case.expected_output, result['output']):
                            test_status = 'accepted'
                            score = 10
                            total_score += score
                        else:
                            test_status = 'wrong_answer'
                            final_status = 'wrong_answer'
                            score = 0
                    else:
                        test_status = result['status']
                        final_status = result['status']
                        score = 0
                    
                    test_results.append({
                        'test_case_id': test_case.id,
                        'input': test_case.input_data,
                        'expected_output': test_case.expected_output,
                        'actual_output': result['output'],
                        'status': test_status,
                        'score': score,
                        'time_used': result['time_used'],
                        'memory_used': result['memory_used'],
                        'error': result['error']
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
                # 清理沙箱环境
                try:
                    import shutil
                    shutil.rmtree(sandbox['temp_dir'])
                except:
                    pass
                    
        except Exception as e:
            return {
                'status': 'system_error',
                'score': 0,
                'error_message': f"系统错误: {str(e)}",
                'test_results': []
            }
    
    def compare_output(self, expected: str, actual: str) -> bool:
        """比较输出结果"""
        expected = expected.strip().replace('\r\n', '\n').replace('\r', '\n')
        actual = actual.strip().replace('\r\n', '\n').replace('\r', '\n')
        return expected == actual
