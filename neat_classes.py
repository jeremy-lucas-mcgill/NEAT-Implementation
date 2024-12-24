import random 
import numpy as np
from copy import deepcopy
class NEAT:
    def __init__(self, input_num, output_num, population_size):
        self.num_species = 1
        self.num_input_nodes = input_num
        self.num_output_nodes = output_num
        self.current_node_id = 0
        self.current_innovation = 0
        self.population_size = population_size
        self.innovation_map = {}
        self.species = []

    def get_innovation_number(self, input_node_id, output_node_id):
        connection_pair = (input_node_id, output_node_id)
        if connection_pair in self.innovation_map:
            return self.innovation_map[connection_pair]
        else:
            self.current_innovation += 1
            self.innovation_map[connection_pair] = self.current_innovation
            return self.current_innovation
    def createNodeGene(self,gene_type, bias):
        self.current_node_id += 1
        return NodeGene (self.current_node_id,gene_type,bias)
    def createConnectionGene(self, input_node, output_node, weight, enabled):
        innovation_num = self.get_innovation_number(input_node,output_node)
        return ConnectionGene(input_node,output_node, weight, enabled, innovation_num)
    def weightMutation(self,parent):
        for gene in parent.connect_genes:
            if random.random() < 0.8:
                gene.weight += random.uniform(-0.1,0.1)
    def connectionMutation(self,parent):
        if random.random() < 0.2:
            input_candidates = [node for node in parent.node_genes if node.gene_type in ['input', 'hidden']]
            output_candidates = [node for node in parent.node_genes if node.gene_type in ['hidden', 'output']]
            if not input_candidates or not output_candidates:
                return
            all_pairs = [(input, output) for input in input_candidates for output in output_candidates]
            unconnected_pairs = [(input, output) for input, output in all_pairs if not any(conn.input_node.id == input.id and conn.output_node.id == output.id for conn in parent.connect_genes)]
            if not unconnected_pairs:
                return
            input_node, output_node = random.choice(unconnected_pairs)
            weight = random.uniform(-1,1)
            new_connect_gene = self.createConnectionGene(input_node, output_node, weight, True)
            parent.connect_genes.append(new_connect_gene)
    def nodeMutation(self,parent):
        if random.random() < 0.05:
            if len(parent.connect_genes) > 0:
                split_conn = random.choice([conn for conn in parent.connect_genes if conn.enabled])
                split_conn.enabled = False
                new_node = self.createNodeGene('hidden',0)
                parent.node_genes.append(new_node)
                input_connection = self.createConnectionGene(split_conn.input_node, new_node, 1, True)
                output_connection = self.createConnectionGene(new_node,split_conn.output_node, 1, True)
                parent.connect_genes.append(input_connection)
                parent.connect_genes.append(output_connection)
    def createOffspring(self,parent1, parent2):
        fitter_parent, other_parent = (parent1,parent2) if parent1.fitness >= parent2.fitness else (parent2, parent1)
        #copy all nodes from fitter parent
        new_node_genes = deepcopy(fitter_parent.node_genes)
        new_connect_genes = []
        #go through all connections from the fitter parent
        for conn in fitter_parent.connect_genes:
            #check if this connection is in both parents by innovation number
            matching_connection = next((conn2 for conn2 in other_parent.connect_genes if conn2.innovation_number == conn.innovation_number), None)

            if matching_connection:
                #inherit randomly
                gene = deepcopy(conn) if random.random() < 0.5 else deepcopy(matching_connection)
                new_connect_genes.append(gene)
            else:
                new_connect_genes.append(deepcopy(conn))
        return Genome(new_node_genes,new_connect_genes)
    def measureCompatibility(self, parent1, parent2, c1=1.0, c2=1.0, c3=0):
        # Get the connection genes of both parents, sorted by innovation number
        genes1 = sorted(parent1.connect_genes, key=lambda g: g.innovation_number)
        genes2 = sorted(parent2.connect_genes, key=lambda g: g.innovation_number)
        # Initialize counts and sums for comparison
        excess_genes = 0
        disjoint_genes = 0
        matching_genes = 0
        total_weight_difference = 0
        # Track the maximum innovation number in each parent
        max_innovation1 = max(g.innovation_number for g in genes1) if genes1 else 0
        max_innovation2 = max(g.innovation_number for g in genes2) if genes2 else 0
        # Use two indices to iterate through both parent connection gene lists
        i, j = 0, 0
        # Loop through the connection genes in both parents
        while i < len(genes1) and j < len(genes2):
            gene1 = genes1[i]
            gene2 = genes2[j]
            if gene1.innovation_number == gene2.innovation_number:
                # Matching genes: Compare the weights
                matching_genes += 1
                total_weight_difference += abs(gene1.weight - gene2.weight)
                i += 1
                j += 1
            elif gene1.innovation_number < gene2.innovation_number:
                # Disjoint gene in parent1 (not found in parent2)
                disjoint_genes += 1 if gene1.innovation_number < max_innovation2 else 0
                excess_genes += 1 if gene1.innovation_number > max_innovation2 else 0
                i += 1
            else:
                # Disjoint gene in parent2 (not found in parent1)
                disjoint_genes += 1 if gene2.innovation_number < max_innovation1 else 0
                excess_genes += 1 if gene2.innovation_number > max_innovation1 else 0
                j += 1
        # Any remaining genes in parent1 or parent2 are considered excess
        excess_genes += len(genes1) - i  # Excess genes in parent1
        excess_genes += len(genes2) - j  # Excess genes in parent2
        # Calculate the average weight difference for matching genes
        avg_weight_difference = total_weight_difference / matching_genes if matching_genes > 0 else 0
        # The normalization factor N is the size of the larger genome
        N = max(len(genes1), len(genes2), 1)  # Avoid division by 0
        # Calculate compatibility distance using the formula
        compatibility_distance = (c1 * excess_genes / N) + (c2 * disjoint_genes / N) + (c3 * avg_weight_difference)
        return compatibility_distance
    def placeGenome(self,parent, old_species, new_species):
        isSimilar = False
        for index,list_of_genomes in enumerate(old_species):
            if self.measureCompatibility(parent, list_of_genomes[0]) < 0.7:
                new_species[index].append(parent)
                isSimilar = True
                break
        if not isSimilar:
            new_species.append([parent])
    def __repr__(self) -> str:
        rep = ""
        fitness_list = [[round(genome.fitness,2) for genome in list] for list in self.species]
        max_fitness = [max(list) for list in fitness_list]
        for index,species in enumerate(self.species):
            rep += f"Species {index}: " + str(max_fitness[index]) + " "
        return rep
    def applyMutations(self, parent):
        if random.random() < 0.8:
            self.weightMutation(parent)
        if random.random() < 0.2:
            self.connectionMutation(parent)
        if random.random() < 0.05:
            self.nodeMutation(parent)
    def initalizeSpecies(self):
        nodes = []
        connections = []
        for _ in range(self.num_input_nodes):
            nodes.append(self.createNodeGene('input', 0))
        for _ in range(self.num_output_nodes):
            nodes.append(self.createNodeGene('output', 0))
        for _ in range(self.population_size):
            newGenome = Genome(deepcopy(nodes), deepcopy(connections))
            self.placeGenome(newGenome,self.species, self.species)
    def keepFittestGenomes(self):
        new_species = []
        for list in self.species:
            top20 = max(1,int(len(self.species) * 0.2))
            remaining = sorted(list, key=lambda genome: genome.fitness)
            new_species.append(remaining)
        self.species = new_species
    def breedWithinSpecies(self):
        #add of fitness scores for each species to determine how many offspring they should make
        # choose parents based off of fitness
        next_species = [[] for _ in self.species]
        total_fitness_scores = np.zeros(len(self.species))
        for index,list in enumerate(self.species):
            sum = 0
            for g in list:
                sum += g.fitness
            total_fitness_scores[index] = sum/len(list)
        #create proportions and how many each species should produce
        num_to_produce = total_fitness_scores/(np.sum(total_fitness_scores)) * self.population_size
        num_to_produce = [int(x) for x in num_to_produce]
        excess = self.population_size - np.sum(num_to_produce)
        num_to_produce[num_to_produce.index(max(num_to_produce))] += excess
        
        for index,list in enumerate(self.species):
            for i in range(num_to_produce[index]):
                if len(list) == 1:
                    offspring = list[0]
                    self.applyMutations(offspring)
                    self.placeGenome(offspring,self.species,next_species)
                elif len(list) > 1:
                    #choose two parents
                    parents = random.sample(list,2)
                    #create an offspring
                    offspring = self.createOffspring(parents[0], parents[1])
                    self.applyMutations(offspring)
                    self.placeGenome(offspring,self.species,next_species)
        next_species = [s for s in next_species if s]
        self.species = next_species
    def addRandomFitness(self):
        for list in self.species:
            for g in list:
                g.fitness = random.random()

class Genome:
    def __init__(self, node_genes, connect_genes):
        self.node_genes = node_genes
        self.connect_genes = connect_genes
        self.fitness = 0
    
    def __repr__(self) -> str:
        rep = "Genome: "
        for n in self.node_genes:
            rep += repr(n)
        rep += "\n"
        for c in self.connect_genes:
            rep += repr(c)
        return rep

class NodeGene:
    def __init__(self,id,gene_type,bias):
        self.id = id
        self.gene_type = gene_type
        self.bias = bias
        self.output_value = 0
    def __repr__(self) -> str:
        return self.gene_type + " Node: " + str(self.id) + " "

class ConnectionGene:
    def __init__(self, input_node, output_node, weight, enabled, innovation_number):
        self.input_node = input_node
        self.output_node = output_node
        self.weight = weight
        self.enabled = enabled
        self.innovation_number = innovation_number
    def __repr__(self) -> str:
        enabled = "" if self.enabled else " (Disabled)"
        return "Connection" + enabled + ": " + str(self.input_node) + " " + str(self.output_node) + " "