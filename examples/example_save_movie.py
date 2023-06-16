"""
This is a small demo script running a randvis simulation and generating a movie.
"""

from randvis.simulation import DVSim

sim = DVSim((10, 15), 0.1, 12345, '../data')
sim.simulate(100, 1, 5)
sim.make_movie('mp4')
sim.make_movie('gif')
