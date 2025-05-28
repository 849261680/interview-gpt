import sys
import traceback

# 添加当前目录到Python路径
sys.path.insert(0, '.')

try:
    # 尝试导入主应用
    print('正在加载后端主模块...')
    from src.main import app
    print('✅ 后端主模块加载成功!')
except Exception as e:
    print('❌ 后端主模块加载失败:')
    traceback.print_exc()
