"""
面试官工厂测试用例
测试面试官的创建和管理逻辑
"""
import pytest
from unittest.mock import Mock, patch

from src.agents.interviewer_factory import InterviewerFactory
from src.agents.base_interviewer import BaseInterviewer
from src.agents.technical_interviewer import TechnicalInterviewer
from src.agents.hr_interviewer import HRInterviewer
from src.agents.behavioral_interviewer import BehavioralInterviewer


class TestInterviewerFactory:
    """面试官工厂测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 清空缓存
        InterviewerFactory._interviewers.clear()
    
    def test_get_interviewer_success(self):
        """测试成功获取面试官"""
        interviewer = InterviewerFactory.get_interviewer("technical")
        
        assert interviewer is not None
        assert isinstance(interviewer, TechnicalInterviewer)
        assert interviewer.role == "技术面试官"
    
    def test_get_interviewer_caching(self):
        """测试面试官实例缓存"""
        # 第一次获取
        interviewer1 = InterviewerFactory.get_interviewer("technical")
        
        # 第二次获取应该返回同一个实例
        interviewer2 = InterviewerFactory.get_interviewer("technical")
        
        assert interviewer1 is interviewer2
    
    def test_get_interviewer_different_types(self):
        """测试获取不同类型的面试官"""
        technical = InterviewerFactory.get_interviewer("technical")
        hr = InterviewerFactory.get_interviewer("hr")
        behavioral = InterviewerFactory.get_interviewer("behavioral")
        
        assert isinstance(technical, TechnicalInterviewer)
        assert isinstance(hr, HRInterviewer)
        assert isinstance(behavioral, BehavioralInterviewer)
        
        # 确保它们是不同的实例
        assert technical is not hr
        assert hr is not behavioral
    
    def test_get_interviewer_invalid_type(self):
        """测试获取无效类型的面试官"""
        with pytest.raises(ValueError) as exc_info:
            InterviewerFactory.get_interviewer("invalid_type")
        
        assert "无效的面试官类型" in str(exc_info.value)
        assert "invalid_type" in str(exc_info.value)
    
    def test_get_all_interviewer_types(self):
        """测试获取所有面试官类型"""
        types = InterviewerFactory.get_all_interviewer_types()
        
        assert isinstance(types, dict)
        assert "technical" in types
        assert "hr" in types
        assert "behavioral" in types
        
        # 验证描述
        assert types["technical"] == "技术面试官"
        assert types["hr"] == "HR面试官"
        assert types["behavioral"] == "行为面试官"
    
    def test_get_interviewer_sequence(self):
        """测试获取面试官顺序"""
        sequence = InterviewerFactory.get_interviewer_sequence()
        
        assert isinstance(sequence, list)
        assert len(sequence) > 0
        assert "technical" in sequence
        assert "behavioral" in sequence
        assert "hr" in sequence
        
        # 验证顺序（技术面试通常在前面）
        assert sequence.index("technical") < sequence.index("hr")
    
    def test_multiple_interviewer_instances(self):
        """测试多个面试官实例的独立性"""
        # 获取所有类型的面试官
        interviewers = {}
        for interviewer_type in ["technical", "hr", "behavioral"]:
            interviewers[interviewer_type] = InterviewerFactory.get_interviewer(interviewer_type)
        
        # 验证每个面试官都有独立的属性
        for interviewer_type, interviewer in interviewers.items():
            assert interviewer.role is not None
            assert interviewer.name is not None
            assert interviewer.description is not None
        
        # 验证不同面试官的角色不同
        roles = [interviewer.role for interviewer in interviewers.values()]
        assert len(set(roles)) == len(roles)  # 所有角色都应该不同


class TestInterviewerFactoryEdgeCases:
    """面试官工厂边界情况测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 清空缓存
        InterviewerFactory._interviewers.clear()
    
    def test_factory_state_isolation(self):
        """测试工厂状态隔离"""
        # 在一个"会话"中创建面试官
        interviewer1 = InterviewerFactory.get_interviewer("technical")
        
        # 清空缓存模拟新会话
        InterviewerFactory._interviewers.clear()
        
        # 在新"会话"中创建同类型面试官
        interviewer2 = InterviewerFactory.get_interviewer("technical")
        
        # 应该是不同的实例
        assert interviewer1 is not interviewer2
        assert type(interviewer1) == type(interviewer2)
    
    def test_concurrent_access(self):
        """测试并发访问"""
        import threading
        import time
        
        results = {}
        errors = []
        
        def get_interviewer(thread_id):
            try:
                time.sleep(0.01)  # 模拟一些处理时间
                interviewer = InterviewerFactory.get_interviewer("technical")
                results[thread_id] = interviewer
            except Exception as e:
                errors.append(e)
        
        # 创建多个线程同时获取面试官
        threads = []
        for i in range(5):
            thread = threading.Thread(target=get_interviewer, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        assert len(errors) == 0, f"出现错误: {errors}"
        assert len(results) == 5
        
        # 所有线程应该获得同一个实例（由于缓存）
        first_interviewer = list(results.values())[0]
        for interviewer in results.values():
            assert interviewer is first_interviewer
    
    @patch('src.agents.interviewer_factory.TechnicalInterviewer')
    def test_interviewer_creation_failure(self, mock_technical):
        """测试面试官创建失败的情况"""
        # 模拟面试官创建时抛出异常
        mock_technical.side_effect = Exception("面试官初始化失败")
        
        with pytest.raises(Exception) as exc_info:
            InterviewerFactory.get_interviewer("technical")
        
        assert "面试官初始化失败" in str(exc_info.value)
    
    def test_factory_type_mapping_integrity(self):
        """测试工厂类型映射的完整性"""
        # 验证所有映射的类型都是BaseInterviewer的子类
        for interviewer_type, interviewer_class in InterviewerFactory._interviewer_types.items():
            assert issubclass(interviewer_class, BaseInterviewer)
            
            # 验证可以成功实例化
            try:
                instance = interviewer_class()
                assert hasattr(instance, 'name')
                assert hasattr(instance, 'role')
                assert hasattr(instance, 'description')
            except Exception as e:
                pytest.fail(f"无法实例化 {interviewer_type}: {e}")


class TestInterviewerFactoryIntegration:
    """面试官工厂集成测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        InterviewerFactory._interviewers.clear()
    
    def test_full_interview_workflow(self):
        """测试完整的面试流程"""
        sequence = InterviewerFactory.get_interviewer_sequence()
        interviewers = []
        
        # 按顺序获取所有面试官
        for interviewer_type in sequence:
            interviewer = InterviewerFactory.get_interviewer(interviewer_type)
            interviewers.append(interviewer)
        
        # 验证面试官序列
        assert len(interviewers) == len(sequence)
        
        # 验证每个面试官都有必要的方法
        for interviewer in interviewers:
            assert hasattr(interviewer, 'generate_response')
            assert hasattr(interviewer, 'generate_questions')
            assert hasattr(interviewer, 'generate_feedback')
    
    def test_interviewer_factory_reset(self):
        """测试面试官工厂重置"""
        # 创建一些面试官实例
        InterviewerFactory.get_interviewer("technical")
        InterviewerFactory.get_interviewer("hr")
        
        assert len(InterviewerFactory._interviewers) == 2
        
        # 清空缓存
        InterviewerFactory._interviewers.clear()
        
        assert len(InterviewerFactory._interviewers) == 0
        
        # 重新创建应该得到新实例
        new_technical = InterviewerFactory.get_interviewer("technical")
        assert new_technical is not None 