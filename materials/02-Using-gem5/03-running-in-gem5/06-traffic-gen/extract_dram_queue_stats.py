import re
import csv
import sys

def extract_queue_histograms(stats_file, output_csv):
    """
    Extract DRAM controller read and write queue length PDF histogram data from gem5 stats file
    and write it to a CSV file.

    Args:
        stats_file (str): Path to the gem5 stats.txt file
        output_csv (str): Path to the output CSV file
    """
    # Dictionary to store histogram data for each memory controller
    mem_controllers = {}

    # Regular expressions to match queue length PDF entries
    # These patterns match lines like: system.mem_ctrl0.rdQLenPdf::40  75  # What read queue...
    rd_pattern = r'system\.(mem_ctrl\d+)\.rdQLenPdf::(\d+)\s+(\d+)'
    wr_pattern = r'system\.(mem_ctrl\d+)\.wrQLenPdf::(\d+)\s+(\d+)'

    try:
        with open(stats_file, 'r') as f:
            for line in f:
                # Check for read queue matches
                rd_match = re.search(rd_pattern, line)
                if rd_match:
                    controller = rd_match.group(1)
                    queue_length = int(rd_match.group(2))
                    count = int(rd_match.group(3))

                    if controller not in mem_controllers:
                        mem_controllers[controller] = {'read': {}, 'write': {}}

                    mem_controllers[controller]['read'][queue_length] = count
                    continue

                # Check for write queue matches
                wr_match = re.search(wr_pattern, line)
                if wr_match:
                    controller = wr_match.group(1)
                    queue_length = int(wr_match.group(2))
                    count = int(wr_match.group(3))

                    if controller not in mem_controllers:
                        mem_controllers[controller] = {'read': {}, 'write': {}}

                    mem_controllers[controller]['write'][queue_length] = count

        # If no data found
        if not mem_controllers:
            print(f"No queue length PDF data found in {stats_file}")
            return

        # Prepare data for CSV
        # Find the maximum queue length across all controllers for both read and write
        max_queue_length = 0
        for controller_data in mem_controllers.values():
            if controller_data['read'] and max(controller_data['read'].keys(), default=0) > max_queue_length:
                max_queue_length = max(controller_data['read'].keys())
            if controller_data['write'] and max(controller_data['write'].keys(), default=0) > max_queue_length:
                max_queue_length = max(controller_data['write'].keys())

        # Write to CSV
        with open(output_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write header row
            controllers = sorted(mem_controllers.keys())
            header = ['Queue Length']
            for controller in controllers:
                header.append(f"{controller}_read")
                header.append(f"{controller}_write")
            writer.writerow(header)

            # Write data rows
            for queue_len in range(max_queue_length + 1):
                row = [queue_len]
                for controller in controllers:
                    row.append(mem_controllers[controller]['read'].get(queue_len, 0))
                    row.append(mem_controllers[controller]['write'].get(queue_len, 0))
                writer.writerow(row)

        print(f"Successfully wrote queue length histogram data to {output_csv}")

    except FileNotFoundError:
        print(f"Error: File {stats_file} not found")
    except Exception as e:
        print(f"Error processing file: {e}")

def create_separate_csvs(stats_file, rd_output_csv, wr_output_csv):
    """
    Extract DRAM controller read and write queue length PDF histogram data from gem5 stats file
    and write them to separate CSV files.

    Args:
        stats_file (str): Path to the gem5 stats.txt file
        rd_output_csv (str): Path to the output CSV file for read queue data
        wr_output_csv (str): Path to the output CSV file for write queue data
    """
    # Dictionary to store histogram data for each memory controller
    mem_controllers = {}

    # Regular expressions to match queue length PDF entries
    rd_pattern = r'system\.(mem_ctrl\d+)\.rdQLenPdf::(\d+)\s+(\d+)'
    wr_pattern = r'system\.(mem_ctrl\d+)\.wrQLenPdf::(\d+)\s+(\d+)'

    try:
        with open(stats_file, 'r') as f:
            for line in f:
                # Check for read queue matches
                rd_match = re.search(rd_pattern, line)
                if rd_match:
                    controller = rd_match.group(1)
                    queue_length = int(rd_match.group(2))
                    count = int(rd_match.group(3))

                    if controller not in mem_controllers:
                        mem_controllers[controller] = {'read': {}, 'write': {}}

                    mem_controllers[controller]['read'][queue_length] = count
                    continue

                # Check for write queue matches
                wr_match = re.search(wr_pattern, line)
                if wr_match:
                    controller = wr_match.group(1)
                    queue_length = int(wr_match.group(2))
                    count = int(wr_match.group(3))

                    if controller not in mem_controllers:
                        mem_controllers[controller] = {'read': {}, 'write': {}}

                    mem_controllers[controller]['write'][queue_length] = count

        # If no data found
        if not mem_controllers:
            print(f"No queue length PDF data found in {stats_file}")
            return

        # Process read queue data
        max_rd_queue_length = 0
        for controller_data in mem_controllers.values():
            if controller_data['read'] and max(controller_data['read'].keys(), default=0) > max_rd_queue_length:
                max_rd_queue_length = max(controller_data['read'].keys())

        with open(rd_output_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write header row
            header = ['Queue Length'] + sorted(mem_controllers.keys())
            writer.writerow(header)

            # Write data rows
            for queue_len in range(max_rd_queue_length + 1):
                row = [queue_len]
                for controller in sorted(mem_controllers.keys()):
                    row.append(mem_controllers[controller]['read'].get(queue_len, 0))
                writer.writerow(row)

        print(f"Successfully wrote read queue length histogram data to {rd_output_csv}")

        # Process write queue data
        max_wr_queue_length = 0
        for controller_data in mem_controllers.values():
            if controller_data['write'] and max(controller_data['write'].keys(), default=0) > max_wr_queue_length:
                max_wr_queue_length = max(controller_data['write'].keys())

        with open(wr_output_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write header row
            header = ['Queue Length'] + sorted(mem_controllers.keys())
            writer.writerow(header)

            # Write data rows
            for queue_len in range(max_wr_queue_length + 1):
                row = [queue_len]
                for controller in sorted(mem_controllers.keys()):
                    row.append(mem_controllers[controller]['write'].get(queue_len, 0))
                writer.writerow(row)

        print(f"Successfully wrote write queue length histogram data to {wr_output_csv}")

    except FileNotFoundError:
        print(f"Error: File {stats_file} not found")
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        # Combined output format
        stats_file = sys.argv[1]
        output_csv = sys.argv[2]
        extract_queue_histograms(stats_file, output_csv)
    elif len(sys.argv) == 4:
        # Separate output files for read and write queues
        stats_file = sys.argv[1]
        rd_output_csv = sys.argv[2]
        wr_output_csv = sys.argv[3]
        create_separate_csvs(stats_file, rd_output_csv, wr_output_csv)
    else:
        print("Usage options:")
        print("1. Combined CSV: python script.py <stats_file> <output_csv>")
        print("   Example: python script.py stats.txt queue_histograms.csv")
        print("2. Separate CSVs: python script.py <stats_file> <read_output_csv> <write_output_csv>")
        print("   Example: python script.py stats.txt rdq_histogram.csv wrq_histogram.csv")
        sys.exit(1)
