from numpy.random import randint as random_integer
from numpy.random import random as random_float
from numpy.random import randn as random_float_neg


class Sampler:
    # static qreal sampledPowerDribble(qreal minPower, qreal maxPower);
    @classmethod
    def sampled_power_dribble(cls, min_power, max_power):
        return (cls.rand_float() * (max_power - min_power) + min_power)
    
    # static qreal sampledPowerKick(qreal minPower, qreal maxPower);
    @classmethod
    def sampled_power_kick(cls, min_power, max_power):
        return (cls.rand_float() * (max_power - min_power) + min_power)
    
    # static Point sampledPointKick(Line target);
    @classmethod
    def sampled_point_kick(cls, target):
        return target    
    
    # static Point sampledPointKickH(Line target);
    # TODO: Colocar uma heuristica para diminuir o espaco de busca do ponto melhor para chutar
    @classmethod
    def sampled_point_kick_h(cls, target):
        return target
    
    # static bool sampledUniformDist(qreal min, qreal max);
    @classmethod
    def sampled_uniform_dist(cls, min, max):
        return (cls.rand_float() <= max) and (cls.rand_float() >= min)
    
    # static qreal randFloat(); //entre 0 e 1
    @classmethod
    def rand_float(cls):
        return random_float()
    
    # static long randInt(int low, int high);
    @classmethod
    def rand_int(cls, low, high):
        # returns a random value in [low, high]
        return random_integer(low, high + 1)