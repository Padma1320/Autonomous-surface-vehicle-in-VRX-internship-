import subprocess
import threading
import time

# ==========================================================
# REAL VRX-STYLE THRUSTER CONTROLLER
#
# LINEAR DYNAMICS:
#
# m*u_dot = F - du*u
# Izz*r_dot = N - dr*r
#
# ==========================================================

# ==========================================================
# USER INPUTS
# ==========================================================

force_x = 0.0
torque_z = 0.0

# ==========================================================
# COMMAND THREAD
# ==========================================================

def keyboard():

    global force_x
    global torque_z

    while True:

        cmd = input(
            "\n[f=forward | b=backward | r=right | l=left | s=stop | q=quit]\n> "
        )

        # ==================================================
        # FORWARD
        # ==================================================

        if cmd == "f":

            force_x = 35.0

        # ==================================================
        # BACKWARD
        # ==================================================

        elif cmd == "b":

            force_x = -35.0

        # ==================================================
        # RIGHT
        # ==================================================

        elif cmd == "r":

            torque_z = -8.0

        # ==================================================
        # LEFT
        # ==================================================

        elif cmd == "l":

            torque_z = 8.0

        # ==================================================
        # STOP
        # ==================================================

        elif cmd == "s":

            force_x = 0.0
            torque_z = 0.0

        # ==================================================
        # QUIT
        # ==================================================

        elif cmd == "q":

            exit()

# ==========================================================
# START KEYBOARD THREAD
# ==========================================================

threading.Thread(
    target=keyboard,
    daemon=True
).start()

print("\nREAL VRX THRUSTER CONTROLLER STARTED\n")

# ==========================================================
# MAIN LOOP
# ==========================================================

while True:

    cmd = f'''
gz service -s /world/sydney_regatta/apply_link_wrench \
--reqtype gz.msgs.EntityWrench \
--reptype gz.msgs.Boolean \
--timeout 100 \
--req '
entity {{
  name: "my_asv"
  type: MODEL
}}

wrench {{

  force {{
    x: {force_x}
  }}

  torque {{
    z: {torque_z}
  }}

}}

duration {{
  sec: 0
  nsec: 100000000
}}
'
'''

    subprocess.run(
        cmd,
        shell=True
    )

    time.sleep(0.1)
