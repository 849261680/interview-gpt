#!/usr/bin/env python3
"""
AI集成测试运行脚本
提供多种测试运行选项和详细的测试报告
"""
import os
import sys
import argparse
import subprocess
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(cmd, description=""):
    """运行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description or cmd}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"执行时间: {end_time - start_time:.2f}秒")
    print(f"返回码: {result.returncode}")
    
    if result.stdout:
        print(f"\n标准输出:\n{result.stdout}")
    
    if result.stderr:
        print(f"\n标准错误:\n{result.stderr}")
    
    return result.returncode == 0


def check_dependencies():
    """检查测试依赖"""
    print("检查测试依赖...")
    
    required_packages = [
        "pytest",
        "pytest-asyncio", 
        "pytest-timeout",
        "psutil",
        "httpx"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package}")
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install " + " ".join(missing_packages))
        return False
    
    return True


def check_environment():
    """检查环境配置"""
    print("\n检查环境配置...")
    
    # 检查API密钥
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        print(f"✓ DEEPSEEK_API_KEY: {'*' * 8}{deepseek_key[-4:]}")
    else:
        print("⚠ DEEPSEEK_API_KEY: 未配置（将跳过真实API测试）")
    
    # 检查项目结构
    required_paths = [
        "src/services/ai",
        "src/agents",
        "tests/test_services",
        "tests/conftest.py"
    ]
    
    for path in required_paths:
        full_path = project_root / path
        if full_path.exists():
            print(f"✓ {path}")
        else:
            print(f"✗ {path}")
            return False
    
    return True


def run_ai_service_tests():
    """运行AI服务测试"""
    cmd = "python -m pytest tests/test_services/test_ai_integration.py::TestAIServiceManager -v --tb=short"
    return run_command(cmd, "AI服务管理器测试")


def run_crewai_tests():
    """运行CrewAI集成测试"""
    cmd = "python -m pytest tests/test_services/test_ai_integration.py::TestCrewAIIntegration -v --tb=short"
    return run_command(cmd, "CrewAI集成测试")


def run_deepseek_tests():
    """运行DEEPSEEK API测试"""
    cmd = "python -m pytest tests/test_services/test_ai_integration.py::TestDeepSeekClient -v --tb=short"
    return run_command(cmd, "DEEPSEEK API测试")


def run_interviewer_tests():
    """运行面试官集成测试"""
    cmd = "python -m pytest tests/test_services/test_ai_integration.py::TestInterviewerIntegration -v --tb=short"
    return run_command(cmd, "面试官集成测试")


def run_integration_scenarios():
    """运行集成场景测试"""
    cmd = "python -m pytest tests/test_services/test_ai_integration.py::TestIntegrationScenarios -v --tb=short"
    return run_command(cmd, "集成场景测试")


def run_performance_tests():
    """运行性能测试"""
    cmd = "python -m pytest tests/test_services/test_ai_integration.py::TestPerformanceAndLoad -v --tb=short"
    return run_command(cmd, "性能和负载测试")


def run_all_ai_tests():
    """运行所有AI集成测试"""
    cmd = "python -m pytest tests/test_services/test_ai_integration.py -v --tb=short --durations=10"
    return run_command(cmd, "所有AI集成测试")


def run_quick_tests():
    """运行快速测试（跳过慢速测试）"""
    cmd = "python -m pytest tests/test_services/test_ai_integration.py -v --tb=short -m 'not slow'"
    return run_command(cmd, "快速AI集成测试")


def run_with_coverage():
    """运行测试并生成覆盖率报告"""
    cmd = "python -m pytest tests/test_services/test_ai_integration.py --cov=src/services/ai --cov=src/agents --cov-report=html --cov-report=term"
    return run_command(cmd, "AI集成测试（含覆盖率）")


def generate_test_report():
    """生成详细测试报告"""
    cmd = "python -m pytest tests/test_services/test_ai_integration.py --html=reports/ai_integration_report.html --self-contained-html -v"
    
    # 确保报告目录存在
    reports_dir = project_root / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    return run_command(cmd, "生成AI集成测试报告")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI集成测试运行器")
    parser.add_argument("--test-type", choices=[
        "all", "quick", "ai-service", "crewai", "deepseek", 
        "interviewer", "integration", "performance", "coverage", "report"
    ], default="all", help="测试类型")
    parser.add_argument("--skip-checks", action="store_true", help="跳过环境检查")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    print("🤖 AI集成测试运行器")
    print(f"项目路径: {project_root}")
    print(f"测试类型: {args.test_type}")
    
    # 切换到项目目录
    os.chdir(project_root)
    
    # 环境检查
    if not args.skip_checks:
        if not check_dependencies():
            print("\n❌ 依赖检查失败")
            return 1
        
        if not check_environment():
            print("\n❌ 环境检查失败")
            return 1
    
    # 运行测试
    success = True
    
    if args.test_type == "all":
        success = run_all_ai_tests()
    elif args.test_type == "quick":
        success = run_quick_tests()
    elif args.test_type == "ai-service":
        success = run_ai_service_tests()
    elif args.test_type == "crewai":
        success = run_crewai_tests()
    elif args.test_type == "deepseek":
        success = run_deepseek_tests()
    elif args.test_type == "interviewer":
        success = run_interviewer_tests()
    elif args.test_type == "integration":
        success = run_integration_scenarios()
    elif args.test_type == "performance":
        success = run_performance_tests()
    elif args.test_type == "coverage":
        success = run_with_coverage()
    elif args.test_type == "report":
        success = generate_test_report()
    
    # 输出结果
    print(f"\n{'='*60}")
    if success:
        print("🎉 测试完成！所有测试通过")
        return 0
    else:
        print("❌ 测试失败！请检查错误信息")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 