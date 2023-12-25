# -*- encoding: utf8 -*-
import json
import os
import subprocess
import sys
sys.path.append(os.path.abspath("."))
from util.task import Task


class Invocation(object):
    def __init__(self, params):
        self.params = params

    def get_dialect(self, param):
        try:
            rule_json = json.loads(param)
        except Exception as e:
            print(f"参数设置错误，采用默认方言 : {e}")
            return "ansi"
        return rule_json['dialect']

    def scan(self, scan_cmd, sql_json):
        issues = []
        print(scan_cmd)
        process = subprocess.Popen(scan_cmd, shell=False)
        process.wait()
        try:
            with open(sql_json, 'r') as fr:
                results = json.load(fr)
            for result in results:
                filepath = result['filepath']
                for issue in result['violations']:
                    line_no = issue['line_no']
                    line_pso = issue['line_pos']
                    code = issue['code']
                    description = issue['description']
                    issues.append({"path": filepath, "rule": code, "msg": description, "line": line_no, "column": line_pso})
        except Exception as e:
            print(f"解析结果异常 : {e}")
            return []
        return issues

    def run(self):
        incr_scan = self.params["incr_scan"]
        work_dir = os.getcwd()
        diff_env = os.environ.get("DIFF_FILES", None)
        scan_files_env = os.getenv("SCAN_FILES")
        to_scan = []
        if incr_scan or diff_env:
            print("scan_type : incr_scan")
            with open(diff_env, "r") as fr:
                diff_files = json.load(fr)
            for diff in diff_files:
                if diff.endswith('sql'):
                    to_scan.append(diff)
        else:
            print("scan_type : full")
            with open(scan_files_env, "r") as rf:
                scan_files = json.load(rf)
            for file in scan_files:
                if file.endswith('sql'):
                    to_scan.append(file)
        issues = []
        if to_scan:
            rule_list = params["rule_list"]
            for rule in rule_list:
                rule_name = rule["name"]
                rule_params = rule["params"]
                print(f"规则 {rule_name} 参数为 : {rule_params}")
                sql_json = os.path.join(work_dir, rule_name + "_result.json")
                scan_cmd = [
                    'python',
                    'src/sqlfluff',
                    'lint',
                    '--dialect', '%s' % self.get_dialect(rule_params),
                    '--rules', '%s' % rule_name,
                    '--format', 'json',
                    '--write-output', sql_json,
                ]
                scan_cmd.extend(to_scan)
                issues.extend(self.scan(scan_cmd, sql_json))
            with open("result.json", "w") as fp:
                json.dump(issues, fp, indent=2)
        else:
            print("To-be-scanned files is empty :)")
            with open("result.json", "w") as fp:
                json.dump(issues, fp, indent=2)


if __name__ == '__main__':
    print("-- start ...")
    params = Task.get_task_params()
    tool = Invocation(params)
    tool.run()
    print("-- end ...")