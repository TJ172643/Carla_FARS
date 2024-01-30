#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

import glob
import os
import sys
import carla
import random
import time


## FARS CASE Description
## No. 10327
## veh1:
## TRAV_SP:15mph P_CRASH1:11/Turning Left P_CRASH2:15/Turning Left IMPACT1 = 3
## veh2:
## TRAV_SP:45mph P_CRASH1:1/Going Straight P_CRASH2:62/From opposite direction  over left lane line IMPACT1 = 12
## Weather: Clear Time: 12:00 Road: T-Intersection
def main():
    actor_list = []
    client = carla.Client("localhost", 2000)
    client.set_timeout(2.0)
    time.sleep(2)

    world = client.get_world()
    # change map to Town04
    world = client.load_world("Town04")
    # 设置同步模式
    settings = world.get_settings()  # 获取当前世界的设置对象

    try:
        # settings.fixed_delta_seconds = 0.05  # 设置固定的时间步长为0.05秒
        settings.synchronous_mode = True  # 启用同步模式
        # set weather to clear
        world.set_weather(carla.WeatherParameters.ClearNoon)
        blueprint_library = world.get_blueprint_library()
        bp = random.choice(blueprint_library.filter("vehicle.tesla.model3"))
        transform1 = carla.Transform(
            carla.Location(x=242.39, y=-246.20, z=0.2), carla.Rotation(yaw=0)
        )
        transform2 = carla.Transform(
            carla.Location(x=305.73, y=-249.87, z=0.2), carla.Rotation(yaw=180)
        )
        vehicle1 = world.spawn_actor(bp, transform1)
        vehicle2 = world.spawn_actor(bp, transform2)
        # add a spectator
        spectator = world.get_spectator()
        spectator.set_transform(
            carla.Transform(
                carla.Location(x=242.39, y=-246.20, z=70.0), carla.Rotation(pitch=-90)
            )
        )
        # set vehicle1's target velocity as 15mph
        vehicle1.set_target_velocity(carla.Vector3D(x=6.7056, y=0.0, z=0.0))
        # set vehicle2's target speed as 45mph
        vehicle2.set_target_velocity(carla.Vector3D(x=-20.1168, y=0.0, z=0.0))

        actor_list.append(vehicle1)
        actor_list.append(vehicle2)
        print("created %s" % vehicle1.type_id)
        print("created %s" % vehicle2.type_id)
        # detect if vehicle1 in intersection area in tick
        while True:
            world.tick()
            if (
                vehicle1.get_location().x > 246
                and vehicle1.get_location().x < 266
                and vehicle1.get_location().y > -258
                and vehicle1.get_location().y < -238
            ):
                print("vehicle1 in intersection area")
                # vehicle1 turn left
                vehicle1.apply_control(carla.VehicleControl(throttle=0.0, steer=-0.25))

        time.sleep(60)

    finally:
        settings.synchronous_mode = False  # 取消同步模式
        print("destroying actors")
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        print("done.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print("\ndone.")