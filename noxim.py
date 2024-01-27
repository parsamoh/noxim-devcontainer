import argparse
import subprocess
from typing import TypedDict
import matplotlib.pyplot as plt
import decimal


bin_path = "~/noxim/bin/noxim -power ~/noxim/bin/power.yaml -config ~/noxim/config_examples/default_config.yaml"

class Res(TypedDict):
    total_received_packets: int
    average_delay: float
    network_throughput: float
    total_energy: float

alias parser = (out:str) -> Res

def parse_noxim_output(output : str) -> Res:
    data : Res = {}
    lines = output.split('\n')
    for line in lines:
        if 'Total received packets' in line:
            data['total_received_packets'] = int(line.split(': ')[1])
        elif 'Global average delay (cycles)' in line:
            data['average_delay'] = float(line.split(': ')[1])
        elif 'Network throughput (flits/cycle)' in line:
            data['network_throughput'] = float(line.split(': ')[1])
        elif 'Total energy (J)' in line:
            data['total_energy'] = float(line.split(': ')[1])
    return data

type parser_fn = callable([str , Res])

def run_nox(cmd : str , parser : callable[str , Res],bin = bin_path) -> Res  :
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    parsed = parser(result)

    


def run_noxim(load, routing, mesh_size, traffic):
    command = f"{bin_path} -pir {load / 8} poisson -dimx {mesh_size} -dimy {mesh_size} -routing {routing} -traffic {traffic}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout


def frange(x, y, jump):
  while x < y:
    yield x
    x += jump




def main():
    parser = argparse.ArgumentParser(description="Run Noxim simulations and plot results")
    parser.add_argument("routing", help="The routing algorithm to use")
    parser.add_argument("network", help="The network configuration")
    parser.add_argument("traffic", help="The traffic distribution")
    parser.add_argument("start_load", type=float, help="Starting network load")
    parser.add_argument("end_load", type=float, help="Ending network load")
    parser.add_argument("step", type=float, help="Step for load increment")
    
    args = parser.parse_args()

    results = []

    # Run Noxim with different loads and collect data
    # for load in range(args.start_load, args.end_load + 1, args.step):
    loads = list(frange(args.start_load, args.end_load + 0.0001,args.step))
    cnt = 0 
    sz = len(loads)
    for load in loads:
        cnt += 1
        print(f"Running simulation {cnt} of {sz}: load = {load}")
        output = run_noxim(load, args.routing, args.network, args.traffic)
        data = parse_noxim_output(output)
        results.append(data)

    print("Done running simulations")
    print("Results:")
    print(results)

    # print(results)

    # Plotting results
    
    latency = [result['average_delay'] for result in results]
    throughput = [result['network_throughput'] for result in results]


    fig, (ax1, ax2) = plt.subplots(1, 2)

    fig.suptitle(f'{args.routing} Routing, {args.network}*{args.network} Mesh, {args.traffic} Traffic')

    ax1.plot(loads, latency)
    # ax1.xlabel('Network Load')
    # ax1.ylabel('Latency')
    ax1.set_title('Latency')
    
    ax2.plot(loads, throughput)
    # ax2.xlabel('Network Throughput')
    # ax2.ylabel('Throughput')
    ax2.set_title('Throughput')

    fig.set_figwidth(10)
    fig.set_figheight(5)
    plt.savefig(f'{args.routing}_{args.network}_{args.traffic}.png')

if __name__ == "__main__":
    main()
    # print(parse_noxim_output(run_noxim(0.01, "XY", 5, "random")))
