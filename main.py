import sys

import networkx as nx
import matplotlib.pyplot as plt

"""
This class is used to display a resource allocation graph based off an input file.
@author: Josh Eldridge
"""
class ResourceManager:

    """
    Constructors of class to set up instance variables
    """
    def __init__(self, file_name):
        self.step = 0
        self.numberProcesses = 0
        self.numberResources = 0
        self.system_deadlocked = False
        # Strings of each statement
        self.statement_list = []
        # Tuples
        self.request_edges = []
        # Tuples
        self.owned_edges = []
        # Deadlocked processes
        self.deadlocked_processes = []
        # Read input upon construction
        self.read_input(file_name)

    """
    Used to read the input file into our data structures
    """
    def read_input(self, file_name):
        with open(file_name, "r") as f:
            lines = f.readlines()
            self.numberProcesses = int(lines[0].split(" processes")[0])
            self.numberResources = int(lines[1].split(" resources")[0])
            for x in range(2, len(lines)):
                self.statement_list.append(lines[x])
            f.close()

    """
    Used to start the simulation process
    """
    def simulate(self):
        # Set up initial matplotlib settings
        plt.rcParams['toolbar'] = 'None'
        plt.axis('off')
        plt.ion()
        plt.show()
        while self.step < len(self.statement_list):
            if self.system_deadlocked:
                # If system is deadlocked then halt more drawing and parsing
                self.step = len(self.statement_list)
                self.shutdown_prompt()
                break
            # Parse statement into data structure
            self.parse_statement()
            # Show graph for each statement
            self.draw_graph()

    """
    Used to parse each statement from the statement list and update data structures accordingly
    """
    def parse_statement(self):
        statement = self.statement_list[self.step]
        resource_shift = self.numberProcesses

        split_statement = statement.split(" ")

        # Split out statement into a usable format
        process_num = int(split_statement[0][1])
        keyword = split_statement[1]
        resource_num = int(split_statement[2][1]) + resource_shift

        if process_num in self.deadlocked_processes:
            print("p" + str(process_num) + " is deadlocked, ignore statement '" + statement + "'")
        else:
            # Print the current statement
            print(statement)
            # Logic to handle requesting and releasing of resources by processes
            # Release, but not if in deadlocked_processes
            if keyword == 'releases' and (resource_num, process_num) in self.owned_edges:
                self.owned_edges.remove((resource_num, process_num))
                # Check to see if anyone is requesting it
                for x in self.request_edges:
                    if x[1] == resource_num:
                        # Give it to the first process that wants this resource
                        self.owned_edges.append((resource_num, x[0]))
                        print("p" + str(x[0]) + " now holds " + "r" + str(resource_num - resource_shift))
                        # Make sure to remove the process' request
                        self.request_edges.remove(x)
                        break
            # Request, but not if in deadlocked_processes
            elif (process_num, resource_num) not in self.request_edges:
                resource_owned = False
                for x in self.owned_edges:
                    if x[0] == resource_num:
                        resource_owned = True
                        break
                if resource_owned:
                    self.request_edges.append((process_num, resource_num))
                else:
                    self.owned_edges.append((resource_num, process_num))
                    print("p" + str(process_num) + " now holds " + "r" + str(resource_num - resource_shift))

        # Increment step so we move onto the next statement
        self.step += 1

    """
    Each call to this will generate a new resource allocation graph based on the current instance's data structure
    """
    def draw_graph(self):
        graph = nx.DiGraph()
        processes = []
        resources = []
        labels = {}
        for x in range(self.numberProcesses):
            processes.append(x)
            labels[x] = 'p' + str(x)
        for x in range(self.numberResources):
            resources.append(x + self.numberProcesses)
            var = x + self.numberProcesses
            labels[var] = 'r' + str(x)
        graph.add_nodes_from(processes + resources)
        graph.add_edges_from(self.request_edges + self.owned_edges)
        pos = nx.bipartite_layout(graph, nodes=processes, align='horizontal')
        nx.draw_networkx_nodes(graph, pos,
                               nodelist=processes,
                               node_color='r',
                               node_size=600,
                               alpha=1)
        nx.draw_networkx_nodes(graph, pos,
                               nodelist=resources,
                               node_color='g',
                               node_size=600,
                               alpha=1)

        # Process edges
        nx.draw_networkx_edges(graph, pos,
                               edgelist=self.request_edges,
                               width=1, alpha=1, arrows=True, arrowstyle='->', arrowsize=20)
        # Resource edges
        nx.draw_networkx_edges(graph, pos,
                               edgelist=self.owned_edges,
                               width=1, alpha=1, arrows=True, arrowstyle='->', arrowsize=20)
        nx.draw_networkx_labels(graph, pos, labels, font_size=16)

        # Check for and update deadlocked processes
        self.deadlocked_processes = []
        for x in list(nx.simple_cycles(graph)):
            for y in x:
                if y in processes and y not in self.deadlocked_processes:
                    self.deadlocked_processes.append(y)
        if len(self.deadlocked_processes) > 0:
            if len(self.deadlocked_processes) == self.numberProcesses:
                self.system_deadlocked = True
                print("System completely deadlocked, halting program")
            else:
                print("These processes are deadlocked: " + ', '.join(str(x) for x in self.deadlocked_processes))
        # Make sure axis stays gone and set an update interval of 2 seconds
        plt.axis("off")
        plt.pause(2)
        plt.savefig("snapshot" + str(self.step) + ".png")
        self.shutdown_prompt()
        # Need to clear graph so old edges don't show still
        plt.clf()

    def shutdown_prompt(self):
        # If this is the final drawing, give the user a chance to view final graph before closing
        if self.step == len(self.statement_list):
            input("Press enter to finish program...")


if __name__ == '__main__':
    if len(sys.argv) == 2:
        ResourceManager(sys.argv[1]).simulate()
    else:
        print("Please enter a valid input file")
