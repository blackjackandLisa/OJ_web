"""
判题引擎工厂 - 根据配置选择合适的判题引擎
"""
import os
import platform
from django.conf import settings
from .engine import JudgeEngine
from .sandbox_engine import SandboxEngine
from .docker_engine import DockerJudgeEngine


class JudgeEngineFactory:
    """判题引擎工厂"""
    
    @staticmethod
    def create_engine():
        """创建判题引擎实例"""
        # 获取引擎类型配置
        engine_type = getattr(settings, 'JUDGE_ENGINE', 'auto')
        
        # 自动选择引擎
        if engine_type == 'auto':
            if platform.system() == 'Windows':
                # Windows系统使用基础引擎
                return JudgeEngine()
            else:
                # Linux系统优先使用Docker引擎
                try:
                    docker_engine = DockerJudgeEngine()
                    if docker_engine.test_connection():
                        return docker_engine
                    else:
                        return SandboxEngine()
                except:
                    return SandboxEngine()
        
        # 根据配置选择引擎
        elif engine_type == 'docker':
            return DockerJudgeEngine()
        elif engine_type == 'sandbox':
            return SandboxEngine()
        elif engine_type == 'basic':
            return JudgeEngine()
        else:
            # 默认使用基础引擎
            return JudgeEngine()
    
    @staticmethod
    def get_available_engines():
        """获取可用的判题引擎列表"""
        engines = ['basic', 'sandbox']
        
        # 检查Docker是否可用
        try:
            docker_engine = DockerJudgeEngine()
            if docker_engine.test_connection():
                engines.append('docker')
        except:
            pass
        
        return engines
    
    @staticmethod
    def test_engine(engine_type: str) -> bool:
        """测试指定引擎是否可用"""
        try:
            if engine_type == 'docker':
                engine = DockerJudgeEngine()
                return engine.test_connection()
            elif engine_type == 'sandbox':
                engine = SandboxEngine()
                return True  # 沙箱引擎总是可用
            elif engine_type == 'basic':
                engine = JudgeEngine()
                return True  # 基础引擎总是可用
            else:
                return False
        except:
            return False
