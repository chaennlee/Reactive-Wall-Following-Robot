#!/usr/bin/env python

import math
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

distance_wall = 0.2
wall_lead = 0.4

g_pub = None
g_sub = None

g_alpha = -1

g_linear_speed = 0.1
g_factor = 1

def update_command_vel(linear_vel, angular_vel):
    msg = Twist()
    msg.linear.x = linear_vel
    msg.angular.z = angular_vel
    g_pub.publish(msg)


def scanCallback(msg):
    scan_max_value = msg.range_max

    regions = {
        'front':  min(msg.ranges[0], scan_max_value),
        'fright':  min(msg.ranges[315], scan_max_value),
        'right':  min(msg.ranges[270], scan_max_value),
        'fleft':  min(msg.ranges[45], scan_max_value),
        'left':  min(msg.ranges[90], scan_max_value),
    }

    global g_alpha, g_linear_speed, g_factor

    g_factor = 1 if regions['front'] > 1 else 2.5

    g_linear_speed = 0.1 if regions['front'] > 2 else regions['front'] / 2 * 0.1

    y0 = regions['right']
    x1 = regions['fright'] * math.sin(math.pi / 4)
    y1 = regions['fright'] * math.cos(math.pi / 4)

    g_alpha = math.atan2(y1 - distance_wall, x1 + wall_lead - y0) - (0 if regions['front'] > 0.5 else 1 - regions['front'])

    print(g_alpha)


if __name__ == '__main__':
    rospy.init_node('wall_following_robot')

    g_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
    g_sub = rospy.Subscriber('/scan', LaserScan, scanCallback)

    rate = rospy.Rate(20)

    while not rospy.is_shutdown():
        update_command_vel(0.1, -(g_alpha))
        rate.sleep()