from stage_env import StageEnv
import random
import numpy as np

env = StageEnv()

obs, _ = env.reset()

step = 0

while True:

    action = random.randint(0, 2)

    obs, reward, done, trunc, info = env.step(action)

    goal_dist = np.sqrt(
        (env.goal_x - env.robot_x) ** 2 +
        (env.goal_y - env.robot_y) ** 2
    )

    print(
        f"Step={step} "
        f"Reward={reward:.3f} "
        f"GoalDist={goal_dist:.2f}"
    )

    step += 1

    if done:

        print("RESET")

        obs, _ = env.reset()