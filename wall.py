class Wall:
    def __init__(self, pos, width, height,speed):
        self.pos = pos
        self.size = [width,height]
        self.speed = speed
        self.timestep = 0

    def update(self):
        self.pos[0] -= self.speed * self.timestep
    
    def set_time_step(self,time_step):
        self.timestep = time_step


