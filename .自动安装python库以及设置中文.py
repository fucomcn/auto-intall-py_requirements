# ==================== 智能依赖安装器 ====================
import subprocess
import sys
import ast
import os
from typing import Set, List

def _get_imports_from_source(source: str) -> Set[str]:
    """从源代码中提取第三方库import"""
    imports = set()
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.level == 0:  # 只处理绝对导入
                    imports.add(node.module.split('.')[0])
    except Exception:
        pass
    return imports

def _get_script_imports() -> Set[str]:
    """获取真正的第三方依赖"""
    # 扩展标准库列表
    stdlibs = {
        'os', 'sys', 're', 'math', 'datetime', 'json', 'collections',
        'pathlib', 'typing', 'ast', 'subprocess', 'importlib', 'inspect',
        'unittest', 'contextlib', 'io', 'queue', 'tkinter', 'textwrap',
        'warnings', '_thread', 'threading', 'pydoc', 'time', 'functools',
        'idlelib', 'linecache', 'atexit', 'traceback', 'pkg_resources',
        '__main__', 'builtins', 'abc', 'argparse', 'array', 'base64',
        'binascii', 'bisect', 'calendar', 'cgi', 'cmd', 'codecs', 'copy',
        'csv', 'ctypes', 'decimal', 'difflib', 'dis', 'doctest', 'email',
        'encodings', 'enum', 'errno', 'faulthandler', 'gc', 'getopt',
        'glob', 'gzip', 'hashlib', 'heapq', 'html', 'http', 'imaplib',
        'itertools', 'locale', 'logging', 'lzma', 'marshal', 'mmap',
        'multiprocessing', 'netrc', 'operator', 'optparse', 'pickle',
        'pprint', 'profile', 'pstats', 'random', 'shutil', 'signal',
        'socket', 'sqlite3', 'ssl', 'stat', 'string', 'struct', 'tempfile',
        'urllib', 'uuid', 'webbrowser', 'zipfile', 'zlib'
    }
    
    imports = set()
    try:
        with open(sys.argv[0], 'r', encoding='utf-8') as f:
            imports.update(_get_imports_from_source(f.read()))
    except Exception:
        pass
    
    return imports - stdlibs

def _get_installed_packages() -> Set[str]:
    """获取已安装的包"""
    try:
        from importlib.metadata import distributions
        return {dist.metadata['Name'].lower() for dist in distributions()}
    except ImportError:
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--format=freeze'],
                capture_output=True, text=True
            )
            return {line.split('==')[0].lower().replace('_', '-') 
                   for line in result.stdout.split('\n') if line}
        except:
            return set()

def _install_packages(packages: Set[str]) -> bool:
    """智能安装依赖包"""
    if not packages:
        return True
    
    # 常见包名映射（如sklearn对应scikit-learn）
    package_map = {
        'sklearn': 'scikit-learn',
        'cv2': 'opencv-python',
        'PIL': 'pillow',
        'yaml': 'pyyaml'
    }
    
    installed = _get_installed_packages()
    to_install = []
    
    for pkg in packages:
        normalized_pkg = pkg.lower().replace('_', '-')
        install_pkg = package_map.get(pkg, pkg)
        
        if (normalized_pkg not in installed and 
            install_pkg.lower().replace('_', '-') not in installed):
            to_install.append(install_pkg)
    
    if not to_install:
        return True
    
    print("\n🔍 检测到需要安装的依赖:", ", ".join(sorted(to_install)))
    print("⏳ 正在自动安装...")
    
    success = True
    for pkg in to_install:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"✅ 成功安装: {pkg}")
        except subprocess.CalledProcessError:
            print(f"❌ 安装失败: {pkg}")
            success = False
    
    if success:
        print("🎉 所有依赖安装完成")
    else:
        print("\n⚠️ 部分依赖安装失败，可以尝试:")
        print("1. 手动安装: pip install 包名")
        print("2. 检查网络连接")
        print("3. 使用管理员权限运行")
    
    return success

# 执行安装（仅当直接运行时）
if __name__ == "__main__":
    if not hasattr(sys, '_auto_deps_installed'):
        required_packages = _get_script_imports()
        if required_packages:
            sys._auto_deps_installed = True
            _install_packages(required_packages)
# ==================== 安装器结束 ====================


# ==================== 智能中文支持 ==================
import matplotlib.pyplot as plt
from matplotlib import font_manager
import matplotlib
import os
import requests
import tempfile
import warnings
from typing import List, Optional

def _get_system_chinese_fonts() -> List[str]:
    """获取系统常见中文字体列表"""
    return [
        'Microsoft YaHei',     # Windows
        'SimHei',              # Windows
        'STHeiti',             # macOS
        'Arial Unicode MS',    # macOS
        'PingFang SC',         # macOS
        'Hiragino Sans GB',    # macOS
        'WenQuanYi Zen Hei',   # Linux
        'Noto Sans CJK SC',    # 跨平台
        'Source Han Sans SC'   # Adobe开源字体
    ]

def _download_font(font_url: str) -> Optional[str]:
    """下载字体文件到临时目录"""
    try:
        response = requests.get(font_url, timeout=10)
        if response.status_code == 200:
            temp_dir = tempfile.gettempdir()
            font_path = os.path.join(temp_dir, os.path.basename(font_url))
            with open(font_path, 'wb') as f:
                f.write(response.content)
            return font_path
    except Exception as e:
        warnings.warn(f"字体下载失败: {e}")
    return None

def _install_simhei_font() -> bool:
    """尝试安装SimHei字体"""
    font_urls = [
        "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Chinese-Simplified/NotoSansCJKsc-Regular.otf",
        "https://raw.githubusercontent.com/googlefonts/noto-cjk/main/Sans/OTF/Chinese-Simplified/NotoSansCJKsc-Regular.otf"
    ]
    
    for url in font_urls:
        font_path = _download_font(url)
        if font_path:
            try:
                font_manager.fontManager.addfont(font_path)
                return True
            except Exception as e:
                warnings.warn(f"字体安装失败: {e}")
    return False

def set_chinese_font(verbose: bool = True) -> bool:
    """
    智能设置中文字体支持
    参数:
        verbose: 是否显示详细信息
    返回:
        bool: 是否成功设置中文字体
    """
    try:
        # 禁用Matplotlib的字体缓存警告
        warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib.font_manager')
        
        # 1. 首先尝试系统已有字体
        available_fonts = [f.name for f in font_manager.fontManager.ttflist]
        chinese_fonts = _get_system_chinese_fonts()
        
        for font in chinese_fonts:
            if font in available_fonts:
                plt.rcParams['font.sans-serif'] = [font]
                plt.rcParams['axes.unicode_minus'] = False
                if verbose:
                    print(f"✅ 已自动设置系统字体: {font}")
                return True
        
        # 2. 尝试使用Matplotlib自带字体
        if 'Arial Unicode MS' in available_fonts:
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False
            if verbose:
                print("✅ 使用Matplotlib自带字体: Arial Unicode MS")
            return True
        
        # 3. 尝试下载安装开源字体
        if _install_simhei_font():
            plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC']
            plt.rcParams['axes.unicode_minus'] = False
            if verbose:
                print("✅ 已安装开源中文字体: Noto Sans CJK SC")
            return True
        
        # 4. 最后尝试回退方案
        plt.rcParams['font.sans-serif'] = ['sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
        warnings.warn("⚠️ 未找到合适的中文字体，中文可能显示异常")
        return False
        
    except Exception as e:
        warnings.warn(f"设置中文字体时出错: {str(e)}")
        return False

# 自动设置中文字体（默认显示详细信息）
if __name__ == "__main__":
    set_chinese_font()
# ==================== 初始化结束 ====================
