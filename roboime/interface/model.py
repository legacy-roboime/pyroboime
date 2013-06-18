"""
This module builds upon a generic physical model for the robots and ball.

This model calculates the Kalman filter based on this model and a data dict
passed from a filter (used in the interface.filter.Kalman).
"""
from .. import options
import numpy


class Model(object):
    """
    This class represents the physical model for a robot or ball in the world.

    It is used to store state variables obtained from update and/or command
    filter.
    """
    def __init__(self, uid):
        self.uid = uid
        self.speeds = (0, 0, 0)
        self.time = None
        # Initialize fixed Kalman matrices
        self.A = numpy.matrix(numpy.eye(3))  # state transition matrix A
        self.H = numpy.matrix(numpy.eye(3))  # observation matrix H
        self.current_state_estimate = numpy.matrix(numpy.zeros((3, 1)))  # initial state x_0
        self.current_prob_estimate = numpy.matrix(numpy.eye(3))  # Initial error probability P matrix
        self.Q = numpy.matrix([  # Q Matrix: estimated error in process.
            [options.Q, 0., 0.],
            [0., options.Q, 0.],
            [0., 0., options.Q]])  # TODO: make different matrix for ball
        self.R = numpy.matrix([  # R Matrix: estimated error in measurements.
            [options.R_var_x, 0, 0],
            [0, options.R_var_y, 0],
            [0, 0, options.R_var_angle]])  # TODO: make different matrix for ball

    def new_speed(self, speeds):
        """
        Store new absolute speeds (speed of the object with the field as
        reference.

        speeds: sequence with 3 elements corresponding to vx (velocity on the
        x axis), vy (velocity on the y axis) and w (angular velocity).
        """
        self.speeds = speeds  # absolute speeds (vx, vy, w)

    def update(self, data):
        """
        Applies the kalman filter.

        data: data dictionary with 'x', 'y' and (for robots) 'angle' keys
        """
        # Time estimation for the first loop
        if self.time:
            timedelta = data['timestamp'] - self.time
        else:
            timedelta = 25e-3  # Estimated loop time (used if unavailable)
            self.time = data['timestamp']
        # Per-step variable vectors
        B = numpy.eye(3) * timedelta  # control matrix B
        # control vector u_n
        control_vector = numpy.matrix(self.speeds).transpose()  # Helps predict based on model
        # measurement vector z_n
        measurement_vector = numpy.matrix([[data['x']], [data['y']], [data.get('angle', 0.)]])

        ####### Kalman Step #######
        #---------------------------Prediction step-----------------------------
        predicted_state_estimate = self.A * self.current_state_estimate + B * control_vector  # x^
        predicted_prob_estimate = (self.A * self.current_prob_estimate) * numpy.transpose(self.A) + self.Q
        #--------------------------Observation step-----------------------------
        innovation = measurement_vector - self.H * predicted_state_estimate  # y~
        innovation_covariance = self.H * predicted_prob_estimate * numpy.transpose(self.H) + self.R  # S
        #-----------------------------Update step-------------------------------
        kalman_gain = predicted_prob_estimate * numpy.transpose(self.H) * numpy.linalg.inv(innovation_covariance)
        self.current_state_estimate = predicted_state_estimate + kalman_gain * innovation
        # We need the size of the matrix so we can make an identity matrix.
        # This is for a more generic procedure (allows more state variables)
        size = self.current_prob_estimate.shape[0]
        # eye(n) = nxn identity matrix.
        self.current_prob_estimate = (numpy.eye(size) - kalman_gain * self.H) * predicted_prob_estimate
        ### Kalman Step finished ###

        # Update data
        data['x'] = self.current_state_estimate[0, 0]
        data['y'] = self.current_state_estimate[1, 0]
        if 'angle' in data:
            data['angle'] = self.current_state_estimate[2, 0]
