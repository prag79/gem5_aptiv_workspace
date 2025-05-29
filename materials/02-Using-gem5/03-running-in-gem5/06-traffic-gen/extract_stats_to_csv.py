import re
import csv
import argparse

def extract_stats(stats_file):
    """
    Extracts CPU, traffic generator, and DRAM latency and bandwidth
    statistics from a gem5 stats.txt file.

    Args:
        stats_file (str): Path to the stats.txt file.

    Returns:
        dict: A dictionary containing the extracted statistics, with units.
    """

    stats = {}

    with open(stats_file, 'r') as f:
        content = f.read()

    # CPU Statistics
    stats['cpu_ipc'] = (extract_stat(content, r"system\.cpu\.ipc\s+([\d\.]+)"), "Instructions per cycle")
    stats['cpu_cpi'] = (extract_stat(content, r"system\.cpu\.cpi\s+([\d\.]+)"), "Cycles per instruction")

    # ICache Statistics
    icache_miss_rate = extract_stat(content, r"system\.cpu\.icache\.overallMissRate::total\s+([\d\.]+)"), "Misses per access"
    stats['icache_miss_rate'] = icache_miss_rate
    icache_avg_miss_latency = extract_stat(content, r"system\.cpu\.icache\.demandAvgMissLatency::total\s+([\d\.]+)"), "ns"
    if icache_avg_miss_latency[0] is not None:
        stats['icache_avg_miss_latency'] = (icache_avg_miss_latency[0] / 1000, "ns") # Convert ticks to ns
    else:
        stats['icache_avg_miss_latency'] = (None, "ns")

    # DCache Statistics
    dcache_miss_rate = extract_stat(content, r"system\.cpu\.dcache\.overallMissRate::total\s+([\d\.]+)"), "Misses per access"
    stats['dcache_miss_rate'] = dcache_miss_rate
    dcache_avg_miss_latency = extract_stat(content, r"system\.cpu\.dcache\.demandAvgMissLatency::total\s+([\d\.]+)"), "ns"
    if dcache_avg_miss_latency[0] is not None:
        stats['dcache_avg_miss_latency'] = (dcache_avg_miss_latency[0] / 1000, "ns") # Convert ticks to ns
    else:
        stats['dcache_avg_miss_latency'] = (None, "ns")

    # Traffic Generator Statistics
    trafficgen_avg_read_latency = extract_stat(content, r"system\.trafficgen\.avgReadLatency\s+([\d\.]+)"), "ns"
    if trafficgen_avg_read_latency[0] is not None:
        stats['trafficgen_avg_read_latency'] = (trafficgen_avg_read_latency[0] / 1000, "ns")  # Convert ticks to ns
    else:
        stats['trafficgen_avg_read_latency'] = (None, "ns")

    trafficgen_avg_write_latency = extract_stat(content, r"system\.trafficgen\.avgWriteLatency\s+([\d\.]+)"), "ns"
    if trafficgen_avg_write_latency[0] is not None:
        stats['trafficgen_avg_write_latency'] = (trafficgen_avg_write_latency[0] / 1000, "ns") # Convert ticks to ns
    else:
        stats['trafficgen_avg_write_latency'] = (None, "ns")

    trafficgen_read_bw = extract_stat(content, r"system\.trafficgen\.readBW\s+([\d\.]+)"), "MB/s"
    if trafficgen_read_bw[0] is not None:
        stats['trafficgen_read_bw'] = (trafficgen_read_bw[0] / 1048576, "MB/s")  # Convert B/s to MB/s
    else:
        stats['trafficgen_read_bw'] = (None, "MB/s")

    trafficgen_write_bw = extract_stat(content, r"system\.trafficgen\.writeBW\s+([\d\.]+)"), "MB/s"
    if trafficgen_write_bw[0] is not None:
        stats['trafficgen_write_bw'] =  (trafficgen_write_bw[0] / 1048576, "MB/s") # Convert B/s to MB/s
    else:
        stats['trafficgen_write_bw'] = (None, "MB/s")

    # DRAM Statistics (Mem_ctrl1)
    dram1_avg_mem_acc_lat = extract_stat(content, r"system\.mem_ctrl1\.dram\.avgMemAccLat\s+([\d\.]+)"), "ns"
    if dram1_avg_mem_acc_lat[0] is not None:
        stats['dram1_avg_mem_acc_lat'] = (dram1_avg_mem_acc_lat[0] / 1000, "ns")  # Convert ticks to ns
    else:
        stats['dram1_avg_mem_acc_lat'] = (None, "ns")

    dram1_avg_rd_bw = extract_stat(content, r"system\.mem_ctrl1\.dram\.bwRead::total\s+([\d\.]+)"), "MB/s"
    if dram1_avg_rd_bw[0] is not None:
        stats['dram1_avg_rd_bw'] = (dram1_avg_rd_bw[0] / 1048576, "MB/s") # Convert B/s to MB/s
    else:
        stats['dram1_avg_rd_bw'] = (None, "MB/s")

    dram1_avg_wr_bw = extract_stat(content, r"system\.mem_ctrl1\.dram\.bwWrite::total\s+([\d\.]+)"), "MB/s"
    if dram1_avg_wr_bw[0] is not None:
        stats['dram1_avg_wr_bw'] = (dram1_avg_wr_bw[0] / 1048576, "MB/s") # Convert B/s to MB/s
    else:
        stats['dram1_avg_wr_bw'] = (None, "MB/s")

    # DRAM Statistics (Mem_ctrl2)
    dram2_avg_mem_acc_lat = extract_stat(content, r"system\.mem_ctrl2\.dram\.avgMemAccLat\s+([\d\.]+)"), "ns"
    if dram2_avg_mem_acc_lat[0] is not None:
        stats['dram2_avg_mem_acc_lat'] = (dram2_avg_mem_acc_lat[0] / 1000, "ns")  # Convert ticks to ns
    else:
        stats['dram2_avg_mem_acc_lat'] = (None, "ns")

    dram2_avg_rd_bw = extract_stat(content, r"system\.mem_ctrl2\.dram\.bwRead::total\s+([\d\.]+)"), "MB/s"
    if dram2_avg_rd_bw[0] is not None:
        stats['dram2_avg_rd_bw'] = (dram2_avg_rd_bw[0] / 1048576, "MB/s") # Convert B/s to MB/s
    else:
        stats['dram2_avg_rd_bw'] = (None, "MB/s")

    dram2_avg_wr_bw =  extract_stat(content, r"system\.mem_ctrl2\.dram\.bwWrite::total\s+([\d\.]+)"), "MB/s"
    if dram2_avg_wr_bw[0] is not None:
        stats['dram2_avg_wr_bw'] = (dram2_avg_wr_bw[0] / 1048576, "MB/s") # Convert B/s to MB/s
    else:
        stats['dram2_avg_wr_bw'] = (None, "MB/s")

    return stats


def extract_stat(content, regex):
    """
    Extracts a single statistic from the stats.txt content using a regular expression.

    Args:
        content (str): The content of the stats.txt file.
        regex (str): The regular expression to use for extraction.

    Returns:
        tuple: (float or None, str): The extracted statistic as a float,
               or None if not found, and the unit of the statistic.
    """
    match = re.search(regex, content)
    if match:
        return float(match.group(1))
    else:
        return None


def save_to_csv(stats, csv_file):
    """
    Saves the extracted statistics to a CSV file.

    Args:
        stats (dict): A dictionary containing the extracted statistics.
        csv_file (str): The path to the CSV file to create.
    """

    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header row
        header = list(stats.keys())
        header_with_units = [f"{key} ({stats[key][1]})" for key in header]  # Add units to header
        writer.writerow(header_with_units)

        # Write data row
        data = [stats[key][0] if stats[key][0] is not None else "N/A" for key in header]  # Handle None values
        writer.writerow(data)


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Extract statistics from a gem5 stats.txt file and save them to a CSV file.")
    parser.add_argument("stats_file", help="Path to the gem5 stats.txt file")
    parser.add_argument("csv_file", help="Path to the output CSV file")

    # Parse command line arguments
    args = parser.parse_args()

    stats_file = args.stats_file
    csv_file = args.csv_file

    extracted_stats = extract_stats(stats_file)

    if extracted_stats:
        print("Extracted Statistics:")
        for key, value in extracted_stats.items():
            if value[0] is not None:
                print(f"{key}: {value[0]} {value[1]}")
            else:
                print(f"{key}: None")

        save_to_csv(extracted_stats, csv_file)
        print(f"Statistics saved to {csv_file}")

    else:
        print("Could not extract statistics.  Check the stats file path and format.")
