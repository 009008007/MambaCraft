/* MambaCraft ARM64 interoperability bridge. Copyright 2026. MIT licensed.
 * No game code, entitlement changes, or authentication hooks.
 * API: minecraft-linux/mcpelauncher-core MinecraftUtils::getApi().
 * Android and Darwin use different signal numbers and sigset_t layouts.
 * Explicitly translate them; never cast an Android mask to a Darwin mask.
 */
typedef unsigned long long mask64;
typedef unsigned int mask32;
typedef __SIZE_TYPE__ usize;
extern void *mcpelauncher_host_dlopen(const char *, int);
extern void *mcpelauncher_host_dlsym(void *, const char *);
extern void mcpelauncher_preinithook(const char *, void *, void **);
extern int mcpelauncher_package_version_code;
extern void *dlopen(const char *, int);
extern void *dlsym(void *, const char *);
extern const char *dlerror(void);
#define PUBLIC __attribute__((visibility("default")))
static int (*native_mask)(int, const mask32 *, mask32 *);
static int (*native_puts)(const char *);
static int (*native_flush)(void *);
static char *(*native_getenv)(const char *);
static int initialized;
/* Darwin fsblkcnt_t/fsfilcnt_t are 32-bit even on arm64. Bionic's are
 * 64-bit. Never pass a guest buffer to the native statvfs function. */
struct darwin_vfs {
 unsigned long bsize, frsize;
 unsigned int blocks, bfree, bavail, files, ffree, favail;
 unsigned long fsid, flag, namemax;
};
struct android_vfs {
 unsigned long bsize, frsize;
 mask64 blocks, bfree, bavail, files, ffree, favail;
 unsigned long fsid, flag, namemax;
 unsigned int reserved[6];
};
_Static_assert(sizeof(struct darwin_vfs)==64,"Darwin arm64 statvfs ABI");
_Static_assert(sizeof(struct android_vfs)==112,"Android arm64 statvfs ABI");
static int (*native_statvfs)(const char *,struct darwin_vfs *);
static int (*native_fstatvfs)(int,struct darwin_vfs *);
static int *(*native_errno)(void);
static int *(*guest_errno)(void);
static const char *instance_dir;
static void (*relocate_symbol)(void *,const char *,void *);
static unsigned int storage_reports;
static void report(const char *);
static int append_path(char *,usize,const char *,const char *);
static int storage_error(int error) {
 if (guest_errno) *guest_errno()=error;
 return -1;
}
static int copy_native_error(void) {
 int error=native_errno?*native_errno():5;
 if(error==63)error=36; /* ENAMETOOLONG */
 if(error==78)error=38; /* ENOSYS */
 if(error==84)error=75; /* EOVERFLOW */
 return storage_error(error);
}
static void convert_vfs(struct android_vfs *out,const struct darwin_vfs *in) {
 out->bsize=in->bsize;out->frsize=in->frsize;
 out->blocks=in->blocks;out->bfree=in->bfree;out->bavail=in->bavail;
 out->files=in->files;out->ffree=in->ffree;out->favail=in->favail;
 out->fsid=in->fsid;out->flag=in->flag;out->namemax=in->namemax;
 for(unsigned int i=0;i<6;i++)out->reserved[i]=0;
}
static int path_prefix(const char *path,const char *prefix) {
 unsigned int i=0;
 while(prefix[i]){if(path[i]!=prefix[i])return 0;i++;}
 return path[i]==0||path[i]=='/';
}
static const char *storage_path(const char *path,char *buffer,usize capacity) {
 const char *prefixes[]={"/data/data/com.mojang.minecraftpe","/data/user/0/com.mojang.minecraftpe","/data/data","/storage/emulated/0","/sdcard","/internal","/external"};
 if(!path)return (const char *)0;
 for(unsigned int i=0;i<sizeof(prefixes)/sizeof(prefixes[0]);i++) {
  if(!path_prefix(path,prefixes[i]))continue;
  const char *suffix=path;const char *p=prefixes[i];while(*p++){suffix++;}
  return append_path(buffer,capacity,instance_dir,suffix)?buffer:(const char *)0;
 }
 return path;
}
static void storage_log(const char *path,mask64 available) {
 /* Inline baseline ARMv8 atomics: avoid introducing compiler-rt's outlined
  * atomic helper and hundreds of unrelated interposable runtime exports. */
 unsigned int previous;
#if defined(__aarch64__)
 unsigned int next,status;
 __asm__ volatile("1: ldxr %w0, [%3]\nadd %w1, %w0, #1\nstxr %w2, %w1, [%3]\ncbnz %w2, 1b"
  : "=&r"(previous),"=&r"(next),"=&r"(status) : "r"(&storage_reports) : "memory");
#else
 previous=__atomic_fetch_add(&storage_reports,1,__ATOMIC_RELAXED);
#endif
 if(previous>=8)return;
 char line[4352],digits[32];unsigned int count=0;
 do{digits[count++]=(char)('0'+available%10);available/=10;}while(available);
 char number[32];for(unsigned int i=0;i<count;i++)number[i]=digits[count-i-1];number[count]=0;
 report("[MambaCompat] Storage query path:");report(path);
 if(append_path(line,sizeof(line),"[MambaCompat] Storage available bytes: ",number))report(line);
}
static int bridge_statvfs(const char *path,struct android_vfs *out) {
 if(!out||!path)return storage_error(14);
 if(!native_statvfs)return storage_error(38);
 char rewritten[4096];const char *actual=storage_path(path,rewritten,sizeof(rewritten));
 if(!actual)return storage_error(36);
 struct darwin_vfs host={0};
 if(native_statvfs(actual,&host)) {
  int result=copy_native_error();report("[MambaCompat] ERROR: storage query failed for path:");report(actual);return result;
 }
 convert_vfs(out,&host);storage_log(actual,(mask64)host.bavail*host.frsize);return 0;
}
static int bridge_fstatvfs(int fd,struct android_vfs *out) {
 if(!out)return storage_error(14);
 if(!native_fstatvfs)return storage_error(38);
 struct darwin_vfs host={0};if(native_fstatvfs(fd,&host))return copy_native_error();
 convert_vfs(out,&host);return 0;
}
static void patch_storage_library(void *library) {
 if(!library||!relocate_symbol)return;
 relocate_symbol(library,"statvfs",(void *)bridge_statvfs);
 relocate_symbol(library,"statvfs64",(void *)bridge_statvfs);
 relocate_symbol(library,"fstatvfs",(void *)bridge_fstatvfs);
 relocate_symbol(library,"fstatvfs64",(void *)bridge_fstatvfs);
}
/* Android/Linux signal -> Darwin signal; 0 denotes no corresponding signal.
 * Real-time signals and SIGPWR cannot be represented on Darwin.
 */
static const unsigned char signals[32] = {
 0,1,2,3,4,5,6,10,8,9,30,11,31,13,14,15,0,20,19,17,18,21,22,16,24,25,26,27,28,23,0,12
};
static int bridge_pthread_sigmask(int how, const mask64 *set, mask64 *oldset) {
 mask32 translated = 0, previous = 0;
 int host_how = 1;
 if (!native_mask) return 38; /* Android ENOSYS */
 if (set) {
  if (how < 0 || how > 2) return 22;
  host_how = how + 1; /* Linux BLOCK=0, UNBLOCK=1, SETMASK=2; Darwin 1,2,3. */
  for (unsigned int sig = 1; sig <= 64; ++sig) {
   if (!(*set & ((mask64)1 << (sig - 1)))) continue;
   if (sig >= 32 || !signals[sig]) return 22;
   translated |= (mask32)1 << (signals[sig] - 1);
  }
 }
 int result = native_mask(host_how, set ? &translated : (const mask32 *)0, oldset ? &previous : (mask32 *)0);
 if (!result && oldset) {
  *oldset = 0;
  for (unsigned int sig = 1; sig < 32; ++sig)
   if (signals[sig] && (previous & ((mask32)1 << (signals[sig] - 1))))
    *oldset |= (mask64)1 << (sig - 1);
 }
 return result;
}
static void report(const char *message) { if (native_puts && message) native_puts(message); if (native_flush) native_flush((void *)0); }
static int append_path(char *out, usize capacity, const char *directory, const char *suffix) {
 usize i=0;
 if (!directory || !*directory) return 0;
 while (*directory) { if (i+1 >= capacity) return 0;out[i++]=*directory++; }
 while (*suffix) { if (i+1 >= capacity) return 0;out[i++]=*suffix++; }
 out[i]=0;return 1;
}
PUBLIC void mod_preinit(void) {
 if (initialized) return;
 initialized=1;
 void *system=mcpelauncher_host_dlopen("/usr/lib/libSystem.B.dylib", 1);
 if (!system) return;
 native_puts=(int (*)(const char *))mcpelauncher_host_dlsym(system,"puts");
 native_flush=(int (*)(void *))mcpelauncher_host_dlsym(system,"fflush");
 native_getenv=(char *(*)(const char *))mcpelauncher_host_dlsym(system,"getenv");
 native_mask=(int (*)(int,const mask32 *,mask32 *))mcpelauncher_host_dlsym(system,"pthread_sigmask");
 native_statvfs=(int (*)(const char *,struct darwin_vfs *))mcpelauncher_host_dlsym(system,"statvfs");
 native_fstatvfs=(int (*)(int,struct darwin_vfs *))mcpelauncher_host_dlsym(system,"fstatvfs");
 native_errno=(int *(*)(void))mcpelauncher_host_dlsym(system,"__error");
 if (mcpelauncher_package_version_code != 972605203 && mcpelauncher_package_version_code != 972113201) {
  report("[MambaCompat] ERROR: package version is not in the integration target list");return;
 }
 if (!native_getenv || !native_mask) {report("[MambaCompat] ERROR: required Darwin interfaces unavailable");return;}
 instance_dir=native_getenv("MAMBACRAFT_INSTANCE_DIR");
 void *api=dlopen("libmcpelauncher_mod.so",0),*libc=dlopen("libc.so",0);
 if(api)relocate_symbol=(void (*)(void *,const char *,void *))dlsym(api,"mcpelauncher_relocate");
 if(libc)guest_errno=(int *(*)(void))dlsym(libc,"__errno");
 if(!native_statvfs||!native_fstatvfs||!native_errno||!guest_errno||!relocate_symbol||!instance_dir||!*instance_dir) {
  report("[MambaCompat] ERROR: required storage interfaces or instance path unavailable");return;
 }
 mcpelauncher_preinithook("statvfs",(void *)bridge_statvfs,(void **)0);
 mcpelauncher_preinithook("statvfs64",(void *)bridge_statvfs,(void **)0);
 mcpelauncher_preinithook("fstatvfs",(void *)bridge_fstatvfs,(void **)0);
 mcpelauncher_preinithook("fstatvfs64",(void *)bridge_fstatvfs,(void **)0);
 /* libc++ implements std::filesystem::space using its own statvfs import.
  * Patching only Minecraft's imports would leave that call on the old shim. */
 void *libcxx=dlopen("libc++_shared.so",0);
 if(!libcxx){report("[MambaCompat] ERROR: libc++ storage bridge could not be installed");report(dlerror());return;}
 patch_storage_library(libcxx);
 report("[MambaCompat] Storage ABI bridge registered for Minecraft and libc++");
 mcpelauncher_preinithook("pthread_sigmask",(void *)bridge_pthread_sigmask,(void **)0);
 const char *names[]={"ldiv","lldiv","imaxdiv"};
 for (unsigned int i=0;i<3;++i) {
  void *symbol=mcpelauncher_host_dlsym(system,names[i]);
  if (!symbol) {report("[MambaCompat] ERROR: required integer division interface unavailable");return;}
  mcpelauncher_preinithook(names[i],symbol,(void **)0);
 }
 report("[MambaCompat] Darwin signal-mask and integer-division hooks registered");
 char path[4096];
 if (!append_path(path,sizeof(path),native_getenv("MAMBACRAFT_COMPAT_DIR"),"/patches/libPlayFabMultiplayer.so")) {
  report("[MambaCompat] ERROR: compatibility directory missing or too long");return;
 }
 /* Standard SDK replacement is loaded before the game's dependency graph.
  * Its SONAME matches the game dependency; original game files stay untouched.
  */
 /* Use the core's own portable mode 0. The macOS guest linker rejects
  * Android's numeric RTLD_GLOBAL=0x100 (observed: invalid flags 102).
  * The dependency is reused by SONAME; RTLD_GLOBAL is unnecessary. */
 void *playfab=dlopen(path,0);
 if (!playfab) {report("[MambaCompat] ERROR: PlayFab preload failed");report(dlerror());return;}
 report("[MambaCompat] READY: official PlayFab SDK preloaded; compatibility bridge active");
}
PUBLIC void mod_init(void) { /* Reapply if the core relocated libc++ during load. */
 if(relocate_symbol)patch_storage_library(dlopen("libc++_shared.so",0));
}
PUBLIC int JNI_OnLoad(void *vm, void *reserved) { (void)vm;(void)reserved;return 0x00010006; }
