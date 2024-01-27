import argparse
import subprocess
import matplotlib.pyplot as plt
import decimal

def frange(x, y, jump):
  while x < y:
    yield x
    x += jump

bin_path = "~/noxim/bin/noxim -power ~/noxim/bin/power.yaml -config ~/noxim/config_examples/default_config.yaml"

def run_noxim(load, routing, mesh_size, traffic):
    command = f"{bin_path} -pir {load / 8} poisson  -dimx {mesh_size} -dimy {mesh_size} -routing {routing} -traffic {traffic}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout



def parse_noxim_output(output):
    data = {}
    
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


def run(routing,network,traffic, loads):
    results = []
    cnt = 0 
    sz = len(loads)
    for load in loads:
        cnt += 1
        print(f"Running simulation {cnt} of {sz}: load = {load}")
        output = run_noxim(load, routing, network, traffic )
        data = parse_noxim_output(output)
        # print(output,data)
        results.append(data)
    return results

def main():
    parser = argparse.ArgumentParser(description="Run Noxim simulations and plot results")
    parser.add_argument("network", help="The network configuration")
    parser.add_argument("traffic", help="The traffic distribution")
    parser.add_argument("start_load", type=float, help="Starting network load")
    parser.add_argument("end_load", type=float, help="Ending network load")
    parser.add_argument("step", type=float, help="Step for load increment")
    
    args = parser.parse_args()

    # Plotting results
    loads = list(frange(args.start_load, args.end_load + 0.0001,args.step))
    lat = []
    thr =[]

    algo = ["XY", "WEST_FIRST" , "ODD_EVEN" , "NEGATIVE_FIRST"]

    for alg in algo : 
        results = run(alg , args.network , args.traffic , loads)
        print(results)
        # print(results)
        lat.append([result['average_delay'] for result in results])
        thr.append([result['network_throughput'] for result in results])


    fig, (ax1, ax2) = plt.subplots(1, 2)

    fig.suptitle(f'{args.network}*{args.network} Mesh, {args.traffic} Traffic')

    for x in range(len(lat)):
        ax1.plot(loads, lat[x], label = f'{algo[x]}')
        ax2.plot(loads, thr[x], label = f'{algo[x]}')

    ax1.set_title('Latency')
    ax2.set_title('Throughput')
    ax1.legend()
    ax2.legend()

    fig.set_figwidth(10)
    fig.set_figheight(5)
    plt.savefig(f'{args.network}_{args.traffic}.png')
    plt.show()

if __name__ == "__main__":
    main()
