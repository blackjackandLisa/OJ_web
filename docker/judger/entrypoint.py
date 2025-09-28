#!/usr/bin/env python3
"""
Docker Judger入口脚本 - 安全的代码执行环境
"""
import os
import sys
import time
import json
import subprocess
import argparse
import resource
import signal
import psutil
from pathlib import Path


def set_resource_limits(time_limit: int, memory_limit: int):
    """设置资源限制"""
    # 设置CPU时间限制（秒）
    resource.setrlimit(resource.RLIMIT_CPU, (time_limit // 1000, time_limit // 1000))
    
    # 设置内存限制（字节）
    memory_bytes = memory_limit * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    
    # 设置文件大小限制
    resource.setrlimit(resource.RLIMIT_FSIZE, (100 * 1024 * 1024, 100 * 1024 * 1024))
    
    # 设置进程数限制
    resource.setrlimit(resource.RLIMIT_NPROC, (50, 50))
    
    # 设置文件描述符限制
    resource.setrlimit(resource.RLIMIT_NOFILE, (100, 100))


def compile_code(code_file: str, language: str) -> tuple[bool, str]:
    """编译代码"""
    if language == 'python':
        return True, ""
    elif language == 'javascript':
        return True, ""
    elif language == 'cpp':
        try:
            result = subprocess.run([
                'g++', '-o', 'solution', code_file,
                '-std=c++17', '-O2', '-Wall', '-Wextra'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True, ""
            else:
                return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, "编译超时"
        except Exception as e:
            return False, f"编译错误: {str(e)}"
    elif language == 'java':
        try:
            result = subprocess.run([
                'javac', code_file
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True, ""
            else:
                return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, "编译超时"
        except Exception as e:
            return False, f"编译错误: {str(e)}"
    else:
        return False, f"不支持的语言: {language}"


def run_code(code_file: str, language: str, input_file: str, 
             time_limit: int, memory_limit: int) -> dict:
    """运行代码"""
    try:
        # 编译代码
        compile_success, compile_error = compile_code(code_file, language)
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
        if language == 'python':
            cmd = ['python3', code_file]
        elif language == 'javascript':
            cmd = ['node', code_file]
        elif language == 'cpp':
            cmd = ['./solution']
        elif language == 'java':
            class_name = Path(code_file).stem
            cmd = ['java', class_name]
        else:
            return {
                'success': False,
                'output': '',
                'error': f'不支持的语言: {language}',
                'time_used': 0,
                'memory_used': 0,
                'status': 'system_error'
            }
        
        # 设置资源限制
        set_resource_limits(time_limit, memory_limit)
        
        # 记录开始时间
        start_time = time.time()
        
        # 启动进程
        process = subprocess.Popen(
            cmd,
            stdin=open(input_file, 'r') if os.path.exists(input_file) else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid
        )
        
        # 监控进程
        max_memory = 0
        
        try:
            # 等待进程完成
            stdout, stderr = process.communicate(timeout=time_limit / 1000.0)
            
            # 计算运行时间
            end_time = time.time()
            run_time = int((end_time - start_time) * 1000)
            
            # 获取内存使用情况
            try:
                process_info = psutil.Process(process.pid)
                max_memory = int(process_info.memory_info().rss / 1024)  # KB
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                max_memory = 0
            
            # 判断状态
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
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                process.wait(timeout=5)
            except:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
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
            'error': f'执行错误: {str(e)}',
            'time_used': 0,
            'memory_used': 0,
            'status': 'system_error'
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Docker Judger')
    parser.add_argument('--language', required=True, help='编程语言')
    parser.add_argument('--code-file', required=True, help='代码文件路径')
    parser.add_argument('--input-file', required=True, help='输入文件路径')
    parser.add_argument('--output-file', required=True, help='输出文件路径')
    parser.add_argument('--error-file', required=True, help='错误文件路径')
    parser.add_argument('--time-limit', type=int, required=True, help='时间限制(ms)')
    parser.add_argument('--memory-limit', type=int, required=True, help='内存限制(MB)')
    
    args = parser.parse_args()
    
    try:
        # 运行代码
        result = run_code(
            args.code_file,
            args.language,
            args.input_file,
            args.time_limit,
            args.memory_limit
        )
        
        # 写入输出文件
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(result['output'])
        
        # 写入错误文件
        with open(args.error_file, 'w', encoding='utf-8') as f:
            f.write(result['error'])
        
        # 输出结果到stdout（JSON格式）
        print(json.dumps({
            'success': result['success'],
            'time_used': result['time_used'],
            'memory_used': result['memory_used'],
            'status': result['status']
        }))
        
        # 根据状态设置退出码
        if result['status'] == 'accepted':
            sys.exit(0)
        elif result['status'] == 'time_limit_exceeded':
            sys.exit(124)
        elif result['status'] == 'memory_limit_exceeded':
            sys.exit(137)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(json.dumps({
            'success': False,
            'time_used': 0,
            'memory_used': 0,
            'status': 'system_error',
            'error': str(e)
        }))
        sys.exit(1)


if __name__ == '__main__':
    main()
