"""Rebuild the shipped ARM64 ELF module with Zig 0.14.1; no Apple SDK needed.
Link-only stubs specify the core's public imports. They are never shipped or
executed; the real core provides these functions at load time.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile
parser=argparse.ArgumentParser();parser.add_argument('--zig',default='zig');args=parser.parse_args()
source=Path(__file__).resolve().parent
output=source.parent/'libmamba_compat.so'
if subprocess.check_output([args.zig,'version'],text=True).strip()!='0.14.1':raise SystemExit('Use Zig 0.14.1 to reproduce this build.')
common=[args.zig,'cc','-target','aarch64-linux-android','-shared','-fPIC','-nostdlib','-fno-stack-protector','-g0']
with tempfile.TemporaryDirectory() as temporary:
    temp=Path(temporary)
    (temp/'api.c').write_text('void*mcpelauncher_host_dlopen(const char*a,int b){return 0;}\nvoid*mcpelauncher_host_dlsym(void*a,const char*b){return 0;}\nvoid mcpelauncher_preinithook(const char*a,void*b,void**c){}\nint mcpelauncher_package_version_code=0;\n')
    (temp/'dl.c').write_text('void*dlopen(const char*a,int b){return 0;}\nvoid*dlsym(void*a,const char*b){return 0;}\nchar*dlerror(void){return 0;}\n')
    for name,filename in [('mcpelauncher_mod','api.c'),('dl','dl.c')]:
        subprocess.run(common+['-Wl,-soname,lib'+name+'.so',str(temp/filename),'-o',str(temp/('lib'+name+'.so'))],check=True)
    subprocess.run(common+['-fno-builtin','-fvisibility=hidden','-mno-outline-atomics','-O2','-Wl,-soname,libmamba_compat.so','-Wl,--no-undefined',str(source/'mamba_compat.c'),'-L'+str(temp),'-lmcpelauncher_mod','-ldl','-o',str(output)],check=True)
print(output)
