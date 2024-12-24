import numpy as np
import math
class Player:
    def __init__(self,genome):
        self.genome = genome
        self.jump_speed = 100
        self.pos = [0,20]
        self.velocity = [0,0]
        self.grav_speed = 100
        self.acceleration = [0,-self.grav_speed]
        self.on_ground = False
        self.last_on_ground = False
        self.closest_wall_distance = 0
        self.score = 0
        self.timestep = 0
        self.size = [10,20]
        self.raycast_num = 5
        self.raycast_distance = 50
        self.raycast_hit = [[0,0] for _  in range(self.raycast_num)]

    def jump(self):
        if self.on_ground:
            self.velocity[1] = self.jump_speed
    def update(self):
        self.score += self.timestep
        if self.on_ground and not self.last_on_ground:
            self.velocity[1] = 0
            self.last_on_ground = True
        if not self.on_ground:
            self.last_on_ground = False
        if self.on_ground:
            self.pos[1] = self.size[1]/2
        self.acceleration[1] = 0 if self.on_ground else -self.grav_speed
        self.velocity[1] = self.velocity[1] + self.acceleration[1] * self.timestep 
        self.pos[1] = self.pos[1] + self.velocity[1] * self.timestep + 0.5 * self.acceleration[1] * self.timestep**2
        if self.forwardPass()[0] > 0.9:
            self.jump()
    def set_time_step(self,time_step):
        self.timestep = time_step
    def output_inputs(self):
        raycasts = [x_pos for (x_pos,y_pos) in self.raycast_hit]
        y_value = self.pos[1]
        outputs = []
        outputs.append(y_value)
        for x in raycasts:
            outputs.append(x)
        return outputs
    def forwardPass(self):
        # Initialize node values dictionary (node.id as key, initialized to 0)
        node_dict = {node.id: 0 for node in self.genome.node_genes}

        # 1. Assign input values to the input nodes (assuming input nodes have ids starting from 1)
        inputs = self.output_inputs()  # Get the input values (e.g., raycast positions, etc.)
        for index, value in enumerate(inputs):
            input_node_id = index + 1  # Assuming input node ids start from 1
            node_dict[input_node_id] = value + self.genome.node_genes[input_node_id - 1].bias

        # 2. Propagate through hidden nodes
        for conn in self.genome.connect_genes:
            if conn.enabled:
                input_node_id = conn.input_node.id
                output_node_id = conn.output_node.id

                # Accumulate the weighted input into the output node
                node_dict[output_node_id] += node_dict[input_node_id] * conn.weight

        # 3. Apply activation function (sigmoid) to hidden and output nodes
        # We need to apply the activation after all inputs have been accumulated
        for node in self.genome.node_genes:
            if node.gene_type != 'input':  # Skip activation for input nodes
                node_dict[node.id] = self.sigmoid(node_dict[node.id] + node.bias)  # Apply bias and sigmoid

        # 4. Collect output node values
        output_nodes = [node for node in self.genome.node_genes if node.gene_type == 'output']
        output = [node_dict[node.id] for node in output_nodes]  # Collect the output values

        return output

    def sigmoid(self, x):
        x = np.clip(x, -500, 500)
        return 1 / (1 + math.exp(-x))
