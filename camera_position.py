class CameraPosition:
    """Camera position class for ease of use with borders and ordering."""

    def __init__(self, name, x, y, z,
                 alpha=0,
                 theta=0,
                 phi=0,
                 x_border_min=0.0,
                 x_border_max=0.0,
                 y_border_min=0.0,
                 y_border_max=0.0):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.alpha = alpha
        self.theta = theta
        self.phi = phi
        self.min_x = x_border_min
        self.max_x = x_border_max
        self.min_y = y_border_min
        self.max_y = y_border_max

    def location(self):
        return [self.x, self.y, self.z]

    def rotation(self):
        return [self.alpha, self.theta, self.phi]

    def borders(self):
        return [self.min_x, self.max_x, self.min_y, self.max_y]
