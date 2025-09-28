"""
Docker判题引擎 - 使用Docker容器进行安全隔离
"""
import os
import json
import time
import docker
import tempfile
import shutil
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from .models import JudgeConfig


class DockerJudgeEngine:
    """Docker判题引擎 - 提供安全的代码执行环境"""
    
    def __init__(self):
        self.client = docker.from_env()
        self.judge_dir = getattr(settings, 'JUDGE_DIR', '/tmp/judge')
        self.sandbox_dir = os.path.join(self.judge_dir, 'sandbox')
        self.ensure_directories()
        
        # Docker镜像配置
        self.judger_image = 'django-oj-judger:latest'
        self.timeout = 30  # 容器超时时间（秒）
        
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
    
    def create_sandbox_files(self, code: str, language: str, test_input: str) -> Dict[str, str]:
        """在沙箱中创建必要的文件"""
        config = self.get_judge_config(language)
        if not config:
            raise ValueError(f"不支持的语言: {language}")
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(dir=self.sandbox_dir)
        
        # 写入用户代码
        code_file = os.path.join(temp_dir, f"solution{config.file_extension}")
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # 写入测试输入
        input_file = os.path.join(temp_dir, "input.txt")
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(test_input or '')
        
        return {
            'temp_dir': temp_dir,
            'code_file': code_file,
            'input_file': input_file,
            'output_file': os.path.join(temp_dir, "output.txt"),
            'error_file': os.path.join(temp_dir, "error.txt")
        }
    
    def run_in_container(self, files: Dict[str, str], language: str, 
                        time_limit: int, memory_limit: int) -> Dict:
        """在Docker容器中运行代码"""
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
            # 构建Docker运行配置
            container_config = {
                'image': self.judger_image,
                'command': [
                    'python', '/app/entrypoint.py',
                    '--language', language,
                    '--code-file', '/sandbox/solution' + config.file_extension,
                    '--input-file', '/sandbox/input.txt',
                    '--output-file', '/sandbox/output.txt',
                    '--error-file', '/sandbox/error.txt',
                    '--time-limit', str(time_limit),
                    '--memory-limit', str(memory_limit)
                ],
                'volumes': {
                    files['temp_dir']: {'bind': '/sandbox', 'mode': 'rw'}
                },
                'mem_limit': f'{memory_limit}m',
                'memswap_limit': f'{memory_limit}m',
                'cpu_quota': 50000,  # 限制CPU使用
                'cpu_period': 100000,
                'network_mode': 'none',  # 禁用网络
                'read_only': True,  # 只读文件系统
                'tmpfs': {
                    '/tmp': 'size=100m,noexec,nosuid,nodev'
                },
                'security_opt': [
                    'no-new-privileges:true',
                    'seccomp:unconfined'  # 可以根据需要配置seccomp
                ],
                'user': 'nobody',  # 非特权用户
                'working_dir': '/sandbox',
                'detach': True,
                'remove': True
            }
            
            # 启动容器
            container = self.client.containers.run(**container_config)
            
            # 等待容器完成
            try:
                result = container.wait(timeout=self.timeout)
                exit_code = result['StatusCode']
                
                # 获取容器日志
                logs = container.logs().decode('utf-8', errors='replace')
                
                # 读取输出文件
                output = ''
                error = ''
                time_used = 0
                memory_used = 0
                
                try:
                    if os.path.exists(files['output_file']):
                        with open(files['output_file'], 'r', encoding='utf-8') as f:
                            output = f.read()
                    
                    if os.path.exists(files['error_file']):
                        with open(files['error_file'], 'r', encoding='utf-8') as f:
                            error = f.read()
                    
                    # 解析时间和内存使用情况
                    if logs:
                        try:
                            log_data = json.loads(logs)
                            time_used = log_data.get('time_used', 0)
                            memory_used = log_data.get('memory_used', 0)
                        except:
                            pass
                            
                except Exception as e:
                    error += f"\n文件读取错误: {str(e)}"
                
                # 判断执行状态
                if exit_code == 0:
                    status = 'accepted'
                elif exit_code == 124:  # timeout
                    status = 'time_limit_exceeded'
                elif exit_code == 137:  # killed
                    status = 'memory_limit_exceeded'
                else:
                    status = 'runtime_error'
                
                return {
                    'success': True,
                    'output': output,
                    'error': error,
                    'time_used': time_used,
                    'memory_used': memory_used,
                    'status': status,
                    'exit_code': exit_code
                }
                
            except docker.errors.NotFound:
                return {
                    'success': False,
                    'output': '',
                    'error': '容器未找到',
                    'time_used': 0,
                    'memory_used': 0,
                    'status': 'system_error'
                }
            except Exception as e:
                return {
                    'success': False,
                    'output': '',
                    'error': f'容器执行错误: {str(e)}',
                    'time_used': 0,
                    'memory_used': 0,
                    'status': 'system_error'
                }
            finally:
                try:
                    container.remove(force=True)
                except:
                    pass
                    
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': f'Docker执行错误: {str(e)}',
                'time_used': 0,
                'memory_used': 0,
                'status': 'system_error'
            }
        finally:
            # 清理临时文件
            try:
                shutil.rmtree(files['temp_dir'])
            except:
                pass
    
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
            
            # 运行测试用例
            test_results = []
            total_score = 0
            max_score = test_cases.count() * 10
            max_time = 0
            max_memory = 0
            final_status = 'accepted'
            
            for test_case in test_cases:
                # 创建沙箱文件
                files = self.create_sandbox_files(
                    submission.code, 
                    submission.language, 
                    test_case.input_data
                )
                
                try:
                    # 在容器中运行代码
                    result = self.run_in_container(
                        files,
                        submission.language,
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
                    
                finally:
                    # 清理文件
                    try:
                        shutil.rmtree(files['temp_dir'])
                    except:
                        pass
            
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
    
    def test_connection(self) -> bool:
        """测试Docker连接"""
        try:
            self.client.ping()
            return True
        except:
            return False
