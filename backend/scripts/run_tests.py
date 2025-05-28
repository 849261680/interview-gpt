#!/usr/bin/env python3
"""
测试运行脚本
提供不同类型的测试运行选项和报告生成
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command: str, description: str = None) -> int:
    """
    运行命令并返回退出码
    
    Args:
        command: 要运行的命令
        description: 命令描述
        
    Returns:
        int: 命令退出码
    """
    if description:
        print(f"\n🔄 {description}")
        print(f"运行命令: {command}")
        print("-" * 50)
    
    result = subprocess.run(command, shell=True)
    return result.returncode


def run_unit_tests():
    """运行单元测试"""
    return run_command(
        "pytest tests/ -m 'unit' --tb=short",
        "运行单元测试"
    )


def run_integration_tests():
    """运行集成测试"""
    return run_command(
        "pytest tests/ -m 'integration' --tb=short",
        "运行集成测试"
    )


def run_api_tests():
    """运行API测试"""
    return run_command(
        "pytest tests/test_api/ --tb=short",
        "运行API测试"
    )


def run_agent_tests():
    """运行面试官测试"""
    return run_command(
        "pytest tests/test_agents/ --tb=short",
        "运行面试官测试"
    )


def run_all_tests():
    """运行所有测试"""
    return run_command(
        "pytest tests/ --tb=short",
        "运行所有测试"
    )


def run_coverage_tests():
    """运行测试并生成覆盖率报告"""
    return run_command(
        "pytest tests/ --cov=src --cov-report=html --cov-report=term-missing",
        "运行测试并生成覆盖率报告"
    )


def run_fast_tests():
    """运行快速测试（排除慢速测试）"""
    return run_command(
        "pytest tests/ -m 'not slow' --tb=line",
        "运行快速测试"
    )


def run_specific_test(test_path: str):
    """运行特定测试文件或测试函数"""
    return run_command(
        f"pytest {test_path} -v",
        f"运行特定测试: {test_path}"
    )


def lint_code():
    """代码质量检查"""
    print("\n🔍 代码质量检查")
    print("-" * 50)
    
    # 检查是否安装了必要的工具
    tools = ["black", "isort", "flake8", "mypy"]
    missing_tools = []
    
    for tool in tools:
        result = subprocess.run(f"which {tool}", shell=True, capture_output=True)
        if result.returncode != 0:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"⚠️  缺少工具: {', '.join(missing_tools)}")
        print("请安装: pip install black isort flake8 mypy")
        return 1
    
    # 运行代码格式化检查
    commands = [
        ("black --check src/", "检查代码格式"),
        ("isort --check-only src/", "检查导入排序"),
        ("flake8 src/", "检查代码风格"),
        ("mypy src/", "检查类型注解")
    ]
    
    for command, description in commands:
        print(f"\n📋 {description}")
        result = subprocess.run(command, shell=True)
        if result.returncode != 0:
            print(f"❌ {description}失败")
            return result.returncode
        else:
            print(f"✅ {description}通过")
    
    return 0


def format_code():
    """格式化代码"""
    print("\n🎨 格式化代码")
    print("-" * 50)
    
    commands = [
        ("black src/", "格式化代码"),
        ("isort src/", "排序导入")
    ]
    
    for command, description in commands:
        result = run_command(command, description)
        if result != 0:
            return result
    
    return 0


def clean_cache():
    """清理缓存文件"""
    print("\n🧹 清理缓存文件")
    print("-" * 50)
    
    # 清理Python缓存
    run_command("find . -type d -name '__pycache__' -exec rm -rf {} +", "清理__pycache__")
    run_command("find . -name '*.pyc' -delete", "清理.pyc文件")
    
    # 清理测试缓存
    run_command("rm -rf .pytest_cache", "清理pytest缓存")
    run_command("rm -rf htmlcov", "清理覆盖率报告")
    run_command("rm -f .coverage", "清理覆盖率数据")
    
    # 清理测试数据库
    run_command("rm -f test.db", "清理测试数据库")
    
    print("✅ 缓存清理完成")
    return 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Interview-GPT 测试运行脚本")
    parser.add_argument(
        "command",
        choices=[
            "unit", "integration", "api", "agents", "all", 
            "coverage", "fast", "lint", "format", "clean"
        ],
        help="要执行的命令"
    )
    parser.add_argument(
        "--test",
        help="运行特定的测试文件或测试函数"
    )
    
    args = parser.parse_args()
    
    # 确保在正确的目录中
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    os.chdir(backend_dir)
    
    print(f"📁 工作目录: {os.getcwd()}")
    
    # 根据命令执行相应的操作
    if args.command == "unit":
        exit_code = run_unit_tests()
    elif args.command == "integration":
        exit_code = run_integration_tests()
    elif args.command == "api":
        exit_code = run_api_tests()
    elif args.command == "agents":
        exit_code = run_agent_tests()
    elif args.command == "all":
        exit_code = run_all_tests()
    elif args.command == "coverage":
        exit_code = run_coverage_tests()
    elif args.command == "fast":
        exit_code = run_fast_tests()
    elif args.command == "lint":
        exit_code = lint_code()
    elif args.command == "format":
        exit_code = format_code()
    elif args.command == "clean":
        exit_code = clean_cache()
    else:
        print(f"❌ 未知命令: {args.command}")
        exit_code = 1
    
    # 如果指定了特定测试
    if args.test:
        exit_code = run_specific_test(args.test)
    
    # 输出结果
    if exit_code == 0:
        print("\n✅ 操作成功完成!")
    else:
        print(f"\n❌ 操作失败，退出码: {exit_code}")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()