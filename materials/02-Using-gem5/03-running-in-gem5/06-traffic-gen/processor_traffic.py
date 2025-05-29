#from m5.objects import System, SrcClockDomain, VoltageDomain, AddrRange, SystemXBar
#from m5.objects import TimingSimpleCPU, TrafficGen
#from m5.objects.DDR4_2400_8x8 import DDR4_2400_8x8
#from m5.objects import Process
import m5
from m5.objects import *
from m5.objects import Cache
from gem5.simulate.simulator import Simulator
from gem5.resources.resource import obtain_resource
#from gem5.components.processors.simple_processor import SimpleProcessor
#from gem5.components.processors.cpu_types import CPUTypes

system = System()

# Set up clock and voltage domains
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Set up memory mode and range
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange(start=0x80000000, size="1GB"),AddrRange(start=0xC0000000, size= "1GB")]  # Example ranges

# Create a system crossbar (bus)
system.membus = SystemXBar()
#system.membus.max_routing_table_size = 4096 # Default is 512, try 1024 or higher


# Create a CPU
system.cpu = ArmTimingSimpleCPU()
system.cpu.icache = Cache(size="32kB", assoc=8,tag_latency=10,
    data_latency=10,
    response_latency=10,
    mshrs=64,
    tgts_per_mshr=20)
system.cpu.dcache = Cache(size="32kB", assoc=8,tag_latency=10,
    data_latency=10,
    response_latency=10,
    mshrs=64,
    tgts_per_mshr=20)

system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port

# Create a Traffic Generator (linear and random)
system.trafficgen = TrafficGen()
system.trafficgen.config_file = "traffic_gen4.cfg"

system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports
# Connect CPU and TrafficGen to the bus
#system.cpu.icache_port = system.membus.cpu_side_ports
#system.cpu.dcache_port = system.membus.cpu_side_ports
system.trafficgen.port = system.membus.cpu_side_ports

system.l2cache = Cache(size="2MB", assoc=8,tag_latency=10,
    data_latency=10,
    response_latency=10,
    mshrs=64,
    tgts_per_mshr=20)


system.cpu.createInterruptController()

system.l2bus = SystemXBar()
#system.l2bus.max_routing_table_size = 4096
system.l2cache.cpu_side = system.membus.mem_side_ports
system.l2cache.mem_side = system.l2bus.cpu_side_ports


# Set up memory controller (LPDDR5) and connect to bus
system.mem_ctrl1 = MemCtrl()
system.mem_ctrl1.dram = LPDDR5_5500_1x16_BG_BL32()
system.mem_ctrl1.dram.range = system.mem_ranges[0]
system.mem_ctrl1.port = system.l2bus.mem_side_ports

system.mem_ctrl2 = MemCtrl()
system.mem_ctrl2.dram = LPDDR5_5500_1x16_BG_BL32()
system.mem_ctrl2.dram.range = system.mem_ranges[1]
system.mem_ctrl2.port = system.l2bus.mem_side_ports

binary_resource = obtain_resource("arm-hello64-static")
binary_path = binary_resource.get_local_path()
print("ARM binary path:", binary_path)

system.workload = SEWorkload.init_compatible(binary_path)
process = Process()
process.cmd = [binary_path]
system.cpu.workload = process
system.cpu.createThreads()

from m5.objects import Root
root = Root(full_system=False, system=system)
import m5
m5.instantiate()


exit_event = m5.simulate(500*1000*1000)
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}.")
m5.stats.dump()
