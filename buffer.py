import argparse
import subprocess
import matplotlib.pyplot as plt
import decimal

def frange(x, y, jump):
  while x < y:
    yield x
    x += jump

bin_path = "~/noxim/bin/noxim -power ~/noxim/bin/power.yaml -config ~/noxim/config_examples/default_config.yaml"

def run_noxim(load, routing, mesh_size, traffic , buffer):
    # Construct the Noxim command with the specified load, algorithm, network, and traffic
    command = f"{bin_path} -pir {load / 8} poisson -buffer {buffer} -dimx {mesh_size} -dimy {mesh_size} -routing {routing} -traffic {traffic}"

    print(command)
    
    # Run the command and capture the output
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


def run(routing,network,traffic, buffer, loads):
    results = []
    cnt = 0 
    sz = len(loads)
    for load in loads:
        cnt += 1
        print(f"Running simulation {cnt} of {sz}: load = {load}")
        output = run_noxim(load, routing, network, traffic , buffer)
        data = parse_noxim_output(output)
        # print(output,data)
        results.append(data)
    return results

def main():
    parser = argparse.ArgumentParser(description="Run Noxim simulations and plot results")
    parser.add_argument("routing", help="The routing algorithm to use")
    parser.add_argument("network", help="The network configuration")
    parser.add_argument("traffic", help="The traffic distribution")
    parser.add_argument("start_load", type=float, help="Starting network load")
    parser.add_argument("end_load", type=float, help="Ending network load")
    parser.add_argument("step", type=float, help="Step for load increment")
    
    args = parser.parse_args()


    # print("Done running simulations")
    # print("Results:")
    # print(results)

    # print(results)

    # Plotting results
    loads = list(frange(args.start_load, args.end_load + 0.0001,args.step))
    lat = []
    thr =[]

    sizes = [2 ,4 , 8]

    for c in sizes : 
        results = run(args.routing , args.network , args.traffic , c , loads)
        # print(results)
        lat.append([result['average_delay'] for result in results])
        thr.append([result['network_throughput'] for result in results])


    fig, (ax1, ax2) = plt.subplots(1, 2)

    fig.suptitle(f'{args.routing} Routing, {args.network}*{args.network} Mesh, {args.traffic} Traffic')

    for x in range(len(lat)):
        ax1.plot(loads, lat[x], label = f'buffer size = {sizes[x]}')
        ax2.plot(loads, thr[x], label = f'buffer size = {sizes[x]}')

    ax1.set_title('Latency')
    ax2.set_title('Throughput')
    ax1.legend()
    ax2.legend()

    fig.set_figwidth(10)
    fig.set_figheight(5)
    plt.savefig(f'{args.routing}_{args.network}_{args.traffic}.png')
    plt.show()

if __name__ == "__main__":
    main()
    # print(parse_noxim_output(run_noxim(0.01, "XY", 5, "random")))
