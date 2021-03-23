#!/usr/bin/env python

import subprocess
import time
from enum import IntEnum
import rospy
from std_msgs.msg import UInt8, Int16, UInt16

class ScriptExecutor(object):
    """Class for executing bash scripts / commands requested by ROS topics"""

    class ExecutionStatus(IntEnum):
        RESET = 0
        INITIALIZED = 1
        PROCESSING = 2
        SUCCESS = 3
        FAILED = 4

    def __init__(self):
        # parameters
        self.script_id_topic_name = rospy.get_param("~script_id_topic_name", "~script_id")
        self.script_argument_topic_name = rospy.get_param("~script_argument_topic_name", "~script_argument")
        self.execution_status_topic_name = rospy.get_param("~execution_status_topic_name", "~execution_status")
        self.sleep_time_in_seconds_between_status_messages = rospy.get_param("~sleep_time_in_seconds_between_status_messages", 1.0)
        self.sleep_time_in_seconds_before_running_script = rospy.get_param("~sleep_time_in_seconds_before_running_script", 0.0)
        self.scripts_directory = rospy.get_param("~scripts_directory")

        # state
        self.script_id_zero_received = False
        self.program_argument = Int16(0)
        self.scripts_configuration = rospy.get_param("~scripts_configuration")

        # publishers
        self.execution_status_publisher = rospy.Publisher(self.execution_status_topic_name, UInt8,
                                                          latch=True, queue_size=5)

        # subscribers
        self.program_id_subscriber = rospy.Subscriber(self.script_id_topic_name, UInt16,
                                                      self.process_program_id)
        self.program_argument_subscriber = rospy.Subscriber(self.script_argument_topic_name, Int16,
                                                            self.process_program_argument)

        self.execution_status_publisher.publish(UInt8(self.ExecutionStatus.RESET))
        time.sleep(self.sleep_time_in_seconds_between_status_messages)
        self.execution_status_publisher.publish(UInt8(self.ExecutionStatus.INITIALIZED))
        time.sleep(self.sleep_time_in_seconds_between_status_messages)

    def process_program_id(self, uint16_msg):
        try:
            if uint16_msg.data == 0:
                rospy.logdebug_throttle(5, "Received script_id: 0 for reset")
                self.script_id_zero_received = True
                return
            if not self.script_id_zero_received:
                rospy.logdebug_throttle(5, "Avoiding script execution because script_id: 0 has not been received yet")
                return
            self.script_id_zero_received = False
            self.execution_status_publisher.publish(UInt8(self.ExecutionStatus.RESET))
            time.sleep(self.sleep_time_in_seconds_between_status_messages)
            self.execution_status_publisher.publish(UInt8(self.ExecutionStatus.PROCESSING))
            time.sleep(self.sleep_time_in_seconds_between_status_messages)
            rospy.loginfo("process_program_id: [%d]", uint16_msg.data)
            if uint16_msg.data > 0 and uint16_msg.data <= len(self.scripts_configuration):
                command = str(self.scripts_configuration[uint16_msg.data - 1])
                command = command.replace("#", str(self.program_argument.data))
                command = command.replace("$", self.scripts_directory + "/")
                rospy.loginfo("command: [%s]", command)
                time.sleep(self.sleep_time_in_seconds_before_running_script)
                result_status = subprocess.call(command, shell=True, executable='/bin/bash')
                rospy.loginfo("command return code: [%s]", result_status)
                if result_status == 0:
                    self.execution_status_publisher.publish(UInt8(self.ExecutionStatus.SUCCESS))
                else:
                    self.execution_status_publisher.publish(UInt8(self.ExecutionStatus.FAILED))
            else:
                rospy.logerr('[script_executor:process_program_id] Received program_id [%s] but it must be > 0 and <= size of scripts_configuration (current size: %s)', str(uint16_msg.data),
                             str(len(self.scripts_configuration)))
                self.execution_status_publisher.publish(UInt8(self.ExecutionStatus.FAILED))
        except Exception as e:
            rospy.logerr('[script_executor:process_program_id] Exception: %s', str(e))
            self.execution_status_publisher.publish(UInt8(self.ExecutionStatus.FAILED))

    def process_program_argument(self, int16_msg):
        try:
            self.program_argument = int16_msg
            rospy.logdebug_throttle(5, "process_program_argument: [%d]", int16_msg.data)
        except Exception as e:
            rospy.logerr('[script_executor:process_program_id] Exception: %s', str(e))
