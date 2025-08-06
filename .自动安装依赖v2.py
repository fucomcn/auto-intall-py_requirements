import subprocess
import sys
import ast
import os
from typing import Set, List

# 标准库列表（支持3.10+动态识别）
try:
    stdlibs = set(sys.stdlib_module_names)
except AttributeError:
    stdlibs = {
        'os', 'sys', 're', 'math', 'datetime', 'json', 'collections',
        'pathlib', 'typing', 'ast', 'subprocess', 'importlib', 'inspect',
        'unittest', 'contextlib', 'io', 'queue', 'textwrap', 'warnings',
        '_thread', 'threading', 'pydoc', 'time', 'functools', 'traceback',
        'pkg_resources', 'argparse', 'array', 'base64', 'binascii', 'bisect',
        'calendar', 'cgi', 'cmd', 'codecs', 'copy', 'csv', 'ctypes', 'decimal',
        'difflib', 'dis', 'doctest', 'email', 'encodings', 'enum', 'errno',
        'faulthandler', 'gc', 'getopt', 'glob', 'gzip', 'hashlib', 'heapq',
        'html', 'http', 'imaplib', 'itertools', 'locale', 'logging', 'lzma',
        'marshal', 'mmap', 'multiprocessing', 'netrc', 'operator', 'optparse',
        'pickle', 'pprint', 'profile', 'pstats', 'random', 'shutil', 'signal',
        'socket', 'sqlite3', 'ssl', 'stat', 'string', 'struct', 'tempfile',
        'urllib', 'uuid', 'webbrowser', 'zipfile', 'zlib'
    }

# 常见模块与 pip 包名映射
package_map = {
    'sklearn': 'scikit-learn',
    'cv2': 'opencv-python',
    'PIL': 'pillow',
    'yaml': 'pyyaml',
    'Image': 'pillow',
    'bs4': 'beautifulsoup4',
    'Crypto': 'pycryptodome',
    'tensorflow': 'tensorflow',
    'torch': 'torch',
    'matplotlib': 'matplotlib',
    'numpy': 'numpy',
    'pandas': 'pandas',
    'requests': 'requests',
    'flask': 'flask',
    'django': 'django'
}

def _get_imports_from_source(source: str) -> Set[str]:
    """从源代码中提取import模块"""
    imports = set()
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.level == 0:
                    imports.add(node.module.split('.')[0])
    except:
        pass
    return imports

def _get_all_py_files(path: str = '.') -> List[str]:
    """递归获取目录下所有.py文件"""
    py_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    return py_files

def _get_all_imports(path: str = '.') -> Set[str]:
    """分析所有.py文件，提取非标准库模块"""
    all_imports = set()
    for file in _get_all_py_files(path):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                source = f.read()
                all_imports.update(_get_imports_from_source(source))
        except:
            continue
    return {i for i in all_imports if i not in stdlibs}

def _get_installed_packages() -> Set[str]:
    """获取系统已安装的pip包名（统一为小写）"""
    try:
        from importlib.metadata import distributions
        return {dist.metadata['Name'].lower() for dist in distributions()}
    except:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=freeze'],
            capture_output=True, text=True
        )
        return {
            line.split('==')[0].lower().replace('_', '-')
            for line in result.stdout.split('\n') if '==' in line
        }

def _install_packages(modules: Set[str], verbose=False) -> bool:
    """安装缺失的第三方包"""
    if not modules:
        print("✅ 无需安装任何新依赖。")
        return True

    installed = _get_installed_packages()
    to_install = []

    for mod in modules:
        install_name = package_map.get(mod, mod)
        pkg_key = install_name.lower().replace('_', '-')
        if pkg_key not in installed:
            to_install.append(install_name)

    if not to_install:
        print("✅ 所有依赖均已安装。")
        return True

    print("\n🔍 需要安装的依赖：", ", ".join(to_install))
    print("⏳ 正在安装，请稍候...\n")

    success = True
    for pkg in to_install:
        print(f"→ 正在安装：{pkg}")
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', pkg],
                stdout=None if verbose else subprocess.DEVNULL,
                stderr=None if verbose else subprocess.DEVNULL
            )
            print(f"✅ 安装成功：{pkg}\n")
        except subprocess.CalledProcessError:
            print(f"❌ 安装失败：{pkg}\n")
            success = False

    if success:
        print("🎉 所有依赖安装完成！")
    else:
        print("⚠️ 部分依赖安装失败，请检查网络或手动安装")

    return success

# 主运行逻辑
if __name__ == '__main__':
    if not hasattr(sys, '_auto_deps_installed'):
        sys._auto_deps_installed = True
        missing = _get_all_imports('.')
        _install_packages(missing, verbose=False)
