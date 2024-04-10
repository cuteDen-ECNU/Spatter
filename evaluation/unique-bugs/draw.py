from matplotlib import pyplot as plt

random_color = '#1289A7'
smart_color = '#A3CB38'

def get_bisect(file_path):
    x = []; y = []
    x_logic = []; y_logic = []
    with open(file_path, 'r') as of:
        lines = of.readlines()
        for i in range(len(lines)):
            line_list = lines[i][:-1].split(',')
            t = float(line_list[2])
            x.append(t - 1) # insert one
            y.append(i) # insert one
            x.append(t)
            y.append(i + 1)
            if line_list[1].strip() == 'logic':
                x_logic.append(t)
                y_logic.append(i + 1)
        x.append(3600) # insert one
        y.append(i + 1) # insert one
    return x, y, x_logic, y_logic


rand = {}    
rand['x'], rand['y'], rand['x_logic'], rand['y_logic'] = get_bisect('doc/unique-bugs/rand-gen-2024-01-10-03/bisection/result.txt')
smart = {}
smart['x'], smart['y'], smart['x_logic'], smart['y_logic'] = get_bisect('doc/unique-bugs/smart-gen-2024-01-08-07/bisection/result.txt')

print(rand)
print(smart)

def plot_bisect(cdt: dict):
    point_sizes = [5 for _ in cdt['x_logic']]
    marker_widths = [10 for _ in cdt['x_logic']]
    # plt.scatter(cdt['x_logic'], cdt['y_logic'], marker='x', color='green', s=point_sizes, linewidths=marker_widths, zorder=2) 
    
    if cdt == rand:
        label = "purely random"
        color = random_color
    else:
        label = "geometry-aware generator"
        color = smart_color

    plt.plot(cdt['x'], cdt['y'], label=label, color=color, marker='o', linewidth=4, markersize=0, zorder=1) 
    plt.yticks(cdt['y'])

plt.figure(figsize=(7,7)) 
plot_bisect(rand)
plot_bisect(smart)

legendsize = 20
titlesize = 28

plt.ylabel('Unique Bugs Number', fontsize=titlesize)
plt.xlabel('Time (s)', fontsize=titlesize)
# plt.legend(fontsize=legendsize)
# plt.grid(True, zorder=0)
plt.tick_params(axis='x', labelsize=legendsize)
plt.tick_params(axis='y', labelsize=legendsize)

plt.tight_layout()
plt.savefig('doc/unique-bugs/unique_bugs.pdf')


#-----------------------------------coverage--------------------
def get_coverage(file_path):
    with open(file_path, 'r') as of:
        lines = of.readlines()
        time = []
        l_c = []
        for l in lines:
            l_list = l.split(',')
            t = float(l_list[0].strip())
            if t < 3600:
                time.append(t)
                l_c.append(float(l_list[1].strip()))
    return time, l_c

def plot_coverage(repo):
    plt.figure(figsize=(8,8)) 
    smart[f"{repo}_time"], smart[f"{repo}_lc"] = get_coverage(f'doc/unique-bugs/smart-gen-2024-01-08-07/coverage/{repo}-2024-01-08-07:50:18.txt')
    rand[f"{repo}_time"], rand[f"{repo}_lc"] = get_coverage(f'doc/unique-bugs/rand-gen-2024-01-10-03/coverage/{repo}-2024-01-10-03:59:36.txt')
    plt.plot(rand[f"{repo}_time"], rand[f"{repo}_lc"], random_color, linewidth=4) 
    plt.plot(smart[f"{repo}_time"], smart[f"{repo}_lc"], smart_color, linewidth=4) 

    # plt.title('Line Coverage of GEOS', fontsize=titlesize)
    plt.xlabel('Time (s)', fontsize=titlesize)
    plt.ylabel('Coverage (%)', fontsize=titlesize)
    # plt.legend(fontsize=legendsize)
    # plt.grid(True)
    plt.tick_params(axis='x', labelsize=legendsize)  
    plt.tick_params(axis='y', labelsize=legendsize)  

    plt.savefig(f'doc/unique-bugs/{repo}_coverage.pdf')

plot_coverage("geos")
plot_coverage("postgis")