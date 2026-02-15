# System Setup

## Table of Contents
- [PREEMPT_RT Kernel](#preempt_rt-kernel)
- [CPU Isolation](#cpu-isolation)
- [IRQ Affinity](#irq-affinity)
- [Kernel Boot Parameters](#kernel-boot-parameters)
- [cgroups v2 for RT](#cgroups-v2-for-rt)
- [Capabilities and Permissions](#capabilities-and-permissions)
- [Kernel Tuning](#kernel-tuning)
- [Complete System Setup Checklist](#complete-system-setup-checklist)

## PREEMPT_RT Kernel

### Status (2025+)
PREEMPT_RT is **fully merged into mainline Linux** as of kernel 6.12 (November 2024). No more out-of-tree patches needed.

### Kernel preemption models

| Config | Latency | Throughput | Use case |
|--------|---------|------------|----------|
| `PREEMPT_NONE` | ~ms | Best | Servers, batch processing |
| `PREEMPT_VOLUNTARY` | ~100s µs | Good | Desktop, general purpose |
| `PREEMPT` | ~10s µs | Moderate | Low-latency applications |
| `PREEMPT_RT` | ~10-50 µs | Lower | Hard real-time, deterministic |

### Enabling PREEMPT_RT
```bash
# Check current kernel:
uname -a
# Look for "PREEMPT_RT" in output

zcat /proc/config.gz | grep PREEMPT
# CONFIG_PREEMPT_RT=y means RT is active

# Building a custom kernel:
make menuconfig
# → General setup → Preemption Model → Fully Preemptible (RT)
```

### Key config options for RT kernel
```
CONFIG_PREEMPT_RT=y
CONFIG_HIGH_RES_TIMERS=y
CONFIG_HZ_1000=y
CONFIG_NO_HZ_FULL=y
CONFIG_RCU_NOCB_CPU=y
CONFIG_CPU_ISOLATION=y
CONFIG_IRQ_FORCED_THREADING=y
```

### What PREEMPT_RT changes
- Most spinlocks become sleeping locks (rt_mutex)
- Interrupt handlers run as kernel threads (can be scheduled)
- Priority inheritance throughout the kernel
- Deterministic wake-up latency

### Distribution RT kernels
```bash
# Ubuntu:
sudo apt install linux-image-lowlatency    # low-latency (not full RT)
sudo pro enable realtime-kernel            # full PREEMPT_RT (Ubuntu Pro)

# RHEL/CentOS:
# Red Hat Enterprise Linux for Real Time (separate subscription)

# Fedora:
# Kernel RT available in Fedora repos
```

## CPU Isolation

Prevent the kernel from scheduling non-RT tasks on specific CPUs.

### Boot parameter
```bash
# In /etc/default/grub:
GRUB_CMDLINE_LINUX="isolcpus=managed_irq,domain,2-7"
# Then: sudo update-grub && reboot
```

### isolcpus flags

| Flag | Effect |
|------|--------|
| (no flag) | Remove CPUs from general scheduler |
| `domain` | Remove CPUs from scheduler load balancing domains |
| `managed_irq` | Prevent managed IRQs on isolated CPUs |

`isolcpus=managed_irq,domain,2-7` is the recommended form — isolates CPUs 2-7 from scheduling and managed IRQs.

### Runtime verification
```bash
# Check isolated CPUs:
cat /sys/devices/system/cpu/isolated

# Check which CPUs a task can run on:
taskset -p $$

# Verify no other tasks on isolated CPUs:
ps -eo pid,psr,comm | awk '$2 >= 2'
```

### cpuset via cgroups (alternative to isolcpus)
```bash
echo "+cpuset" > /sys/fs/cgroup/cgroup.subtree_control
mkdir /sys/fs/cgroup/rt

echo "2-7" > /sys/fs/cgroup/rt/cpuset.cpus
echo "0" > /sys/fs/cgroup/rt/cpuset.mems
echo "root" > /sys/fs/cgroup/rt/cpuset.cpus.partition  # exclusive partition

echo $RT_PID > /sys/fs/cgroup/rt/cgroup.procs
```

## IRQ Affinity

Steer hardware interrupts away from RT CPUs:

```bash
# Pin all IRQs to CPU 0:
# Boot param:
irqaffinity=0

# Runtime — per IRQ:
echo 1 > /proc/irq/42/smp_affinity  # bitmask: CPU 0

# List all IRQs and their affinities:
for irq in /proc/irq/*/smp_affinity; do
    echo "$(dirname $irq | xargs basename): $(cat $irq)"
done

# Disable irqbalance daemon:
sudo systemctl stop irqbalance
sudo systemctl disable irqbalance
```

### Threaded IRQs
With PREEMPT_RT, most IRQ handlers run as kernel threads. You can set their priority:

```bash
# List IRQ threads:
ps -eo pid,cls,rtprio,comm | grep irq/

# Set priority of a specific IRQ thread:
chrt -f -p 90 $(pgrep -f "irq/42")
```

## Kernel Boot Parameters

### Complete RT boot line
```bash
GRUB_CMDLINE_LINUX="isolcpus=managed_irq,domain,2-7 \
    nohz_full=2-7 \
    rcu_nocbs=2-7 \
    irqaffinity=0 \
    skew_tick=1 \
    nosoftlockup \
    tsc=reliable \
    intel_pstate=disable \
    processor.max_cstate=1 \
    idle=poll \
    intel_idle.max_cstate=0 \
    transparent_hugepage=never \
    nowatchdog \
    nmi_watchdog=0"
```

### Parameter reference

| Parameter | Purpose |
|-----------|---------|
| `isolcpus=managed_irq,domain,N-M` | Isolate CPUs from scheduler and IRQs |
| `nohz_full=N-M` | Disable periodic timer tick on isolated CPUs |
| `rcu_nocbs=N-M` | Offload RCU callbacks from isolated CPUs |
| `irqaffinity=0` | Pin IRQs to CPU 0 |
| `skew_tick=1` | Offset timer ticks across CPUs (reduce lock contention) |
| `nosoftlockup` | Disable soft lockup detector (false positives on RT) |
| `nowatchdog` | Disable NMI watchdog |
| `nmi_watchdog=0` | Disable NMI watchdog |
| `tsc=reliable` | Trust TSC (avoid expensive fallback clocks) |
| `intel_pstate=disable` | Disable Intel P-State frequency driver |
| `processor.max_cstate=1` | Prevent deep C-states (reduces wakeup latency) |
| `idle=poll` | Never enter C-states (max power, min latency) |
| `transparent_hugepage=never` | Disable THP compaction (latency spikes) |

### Power management vs latency tradeoff
- `idle=poll` + `processor.max_cstate=1`: Lowest latency, highest power
- Just `processor.max_cstate=1`: Good latency, moderate power
- Default: Variable latency (C-state exit can be 10-200 µs)

## cgroups v2 for RT

### CPU controller
```bash
# Enable CPU controller:
echo "+cpu" > /sys/fs/cgroup/cgroup.subtree_control

# Create RT group:
mkdir /sys/fs/cgroup/rt-app

# Set CPU bandwidth (quota/period in µs):
echo "50000 100000" > /sys/fs/cgroup/rt-app/cpu.max
# 50ms per 100ms = 50% of one CPU

# Set weight (relative to other groups):
echo 10000 > /sys/fs/cgroup/rt-app/cpu.weight  # max weight

echo $PID > /sys/fs/cgroup/rt-app/cgroup.procs
```

### cpuset controller
```bash
echo "+cpuset" > /sys/fs/cgroup/cgroup.subtree_control
mkdir /sys/fs/cgroup/rt-app

echo "2-7" > /sys/fs/cgroup/rt-app/cpuset.cpus
echo "0" > /sys/fs/cgroup/rt-app/cpuset.mems
echo $PID > /sys/fs/cgroup/rt-app/cgroup.procs
```

### Memory controller
```bash
echo "+memory" > /sys/fs/cgroup/cgroup.subtree_control
echo "2G" > /sys/fs/cgroup/rt-app/memory.max     # hard limit
echo "1G" > /sys/fs/cgroup/rt-app/memory.high    # throttle point
echo "512M" > /sys/fs/cgroup/rt-app/memory.low   # protection floor
```

### PSI (Pressure Stall Information)
```bash
# System-wide:
cat /proc/pressure/cpu
cat /proc/pressure/memory
cat /proc/pressure/io

# Per-cgroup:
cat /sys/fs/cgroup/rt-app/cpu.pressure
cat /sys/fs/cgroup/rt-app/memory.pressure

# Output format:
# some avg10=0.00 avg60=0.00 avg300=0.00 total=0
# full avg10=0.00 avg60=0.00 avg300=0.00 total=0
```

## Capabilities and Permissions

### Required capabilities for RT

| Capability | Purpose |
|-----------|---------|
| `CAP_SYS_NICE` | Set RT scheduling policy and priority |
| `CAP_IPC_LOCK` | `mlockall`, `mlock` |
| `CAP_SYS_RAWIO` | Access I/O ports, hardware |
| `CAP_SYS_RESOURCE` | Override resource limits |

### Setting capabilities
```bash
# On the binary:
sudo setcap 'cap_sys_nice,cap_ipc_lock=eip' ./my_rt_app

# Check:
getcap ./my_rt_app

# Remove:
sudo setcap -r ./my_rt_app
```

### PAM limits (alternative)
```bash
# /etc/security/limits.conf:
@realtime hard rtprio 99
@realtime hard memlock unlimited
@realtime hard nice -20

# Add user to realtime group:
sudo usermod -a -G realtime $USER
```

### Systemd service configuration
```ini
[Service]
ExecStart=/usr/local/bin/my_rt_app
AmbientCapabilities=CAP_SYS_NICE CAP_IPC_LOCK
CPUAffinity=2 3 4 5
CPUSchedulingPolicy=fifo
CPUSchedulingPriority=80
LimitMEMLOCK=infinity
LimitRTPRIO=99
```

## Kernel Tuning

### RT-specific sysctls
```bash
# RT throttling — safety valve to prevent RT lockout:
# Default: RT tasks get 950ms per 1000ms period (95%)
cat /proc/sys/kernel/sched_rt_runtime_us   # 950000
cat /proc/sys/kernel/sched_rt_period_us    # 1000000

# Disable RT throttling (dangerous — RT can starve the system):
echo -1 > /proc/sys/kernel/sched_rt_runtime_us

# Timer migration — disable for isolated CPUs:
echo 0 > /proc/sys/kernel/timer_migration
```

### Memory
```bash
# Disable swap for RT (optional — with mlockall this is belt+suspenders):
swapoff -a

# Disable transparent huge pages:
echo never > /sys/kernel/mm/transparent_hugepage/enabled

# Disable compaction (latency spikes):
echo never > /sys/kernel/mm/transparent_hugepage/defrag
```

## Complete System Setup Checklist

### Kernel
- [ ] PREEMPT_RT kernel (6.12+) installed
- [ ] `CONFIG_HZ_1000=y`
- [ ] `CONFIG_HIGH_RES_TIMERS=y`

### Boot parameters
- [ ] `isolcpus=managed_irq,domain,<RT_CPUS>`
- [ ] `nohz_full=<RT_CPUS>`
- [ ] `rcu_nocbs=<RT_CPUS>`
- [ ] `irqaffinity=<NON_RT_CPU>`
- [ ] Power management settings for latency needs

### System services
- [ ] `irqbalance` disabled
- [ ] Unnecessary services stopped on RT system
- [ ] NTP configured (chrony preferred over ntpd for RT)

### Permissions
- [ ] `CAP_SYS_NICE` + `CAP_IPC_LOCK` on binary, OR
- [ ] PAM limits configured for RT user group

### Verification
```bash
# Verify RT capability:
cyclictest -l 100000 -m -S -p 80 -i 200 -h 100 -q
# Look at max latency — should be < 100 µs on well-tuned system

# Check for interference:
hwlatdetect --duration=60
# Reports hardware-induced latency spikes (SMIs, etc.)
```
