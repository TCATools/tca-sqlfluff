# -*- encoding: utf8 -*-
import os
import json

class Task(object):
    @classmethod
    def get_task_params(cls):
        """
        获取任务参数
        """
        task_request_file = os.environ.get("TASK_REQUEST")
        with open(task_request_file, 'r') as fr:
            task_request = json.load(fr)
        task_params = task_request["task_params"]
        return task_params
