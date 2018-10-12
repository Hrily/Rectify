import sys
import os
import subprocess
import shlex

DB = "RectifyTest"
HELP = 'Usage python add_problem.py <folder-name> <problem-id>'

if len(sys.argv) != 3:
    print(HELP)
    sys.exit(0)

def read_and_get(filename):
    file = open(filename, "r")
    return file.read().replace('"', '\"').replace('\'', '\'\\\'\'')

def execute(command):
    # print(command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    out, err = proc.communicate()
    if proc.returncode != 0 or err is not None:
        print(out)
        print(err)
        print("Exiting due to error : {0}".format(proc.returncode))
        sys.exit(proc.returncode)
    return out

def db_insert(file, document, entry):
    f = open('{0}.db_insert'.format(os.path.join(question_folder, file)), 'w')
    f.write("db.{0}.insert({1});".format(document, entry))
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # out = execute("mongo {0} < {1}".format(DB, os.path.join(dir_path, 'db_insert')))
    # print(out)

def remove_duplicate(problem_id):
    print("Removing problem with id {0}".format(problem_id))
    query = '\"problem_id\": \"{0}\"'.format(problem_id)
    query = "{" + query + "}"
    command = "echo 'db.Problems.remove({1});' | mongo {0}".format(
        DB, query)
    execute(command)
    command = "echo 'db.Testcases.remove({1});' | mongo {0}".format(
        DB, query)
    execute(command)
    command = "echo 'db.SystemTests.remove({1});' | mongo {0}".format(
        DB, query)
    execute(command)

def check_for_duplicate(problem_id):
    query = '\"problem_id\": \"{0}\"'.format(problem_id)
    query = "{" + query + "}"
    command = "echo 'db.Problems.find({1});' | mongo {0}".format(
        DB, query)
    out = execute(command)
    if "problem_id" in out:
        choice = raw_input("Problem with id {0} already exists. Do you want to overwrite? [y/N] : ".format(problem_id))
        if choice == "y" or choice == "Y":
            remove_duplicate(problem_id)
        else:
            sys.exit(69)

question_folder = sys.argv[1]
problem_id = sys.argv[2]

check_for_duplicate(problem_id)

name = read_and_get(os.path.join(question_folder, "name.txt"))
statement = read_and_get(os.path.join(question_folder, "statement.txt"))
constraints = read_and_get(os.path.join(question_folder, "constraints.txt"))
code = "" #read_and_get(os.path.join(question_folder, "code.cpp"))
time_limit = read_and_get(os.path.join(question_folder, "time_limit.txt"))
memory_limit = read_and_get(os.path.join(question_folder, "memory_limit.txt"))
nsimple = int(read_and_get(os.path.join(question_folder, "nsimple.txt")))
nsystem = int(read_and_get(os.path.join(question_folder, "nsystem.txt")))

problem_entry = """
{7}
    "_id": "{0}",
    "problem_id": "{0}",
    "problem_name": "{1}",
    "problem_statement": `{2}`,
    "problem_constraints": "{3}",
    "time_constraint": "{4}",
    "memory_constraint": "{5}",
    "correct_code": "{6}"
{8}
""".format(
    problem_id,
    name.replace('\n', ' ').replace('\r', ''),
    statement.replace('\n', '<br/>').replace('\r', ''),
    constraints.replace('\n', '<br/>').replace('\r', ''),
    time_limit.replace('\n', '<br/>').replace('\r', ''),
    memory_limit.replace('\n', '<br/>').replace('\r', ''),
    code.replace('\n', ' '),
    "{",
    "}"
).replace('\n', '')

print("Adding problem to db")

db_insert("problem", "Problems", problem_entry)

for i in range(1, nsimple + 1):
    in_ = read_and_get(os.path.join(question_folder,
                                    "simple", "{0}.in".format(i)))
    out = read_and_get(os.path.join(question_folder,
                                    "simple", "{0}.out".format(i)))
    simple_test_entry = """
    {4}
        "problem_id": "{0}", 
        "input_data": `{1}`,
        "output_data": `{2}`,
        "time_limit": "{3}"
    {5}
    """.format(
        problem_id,
        in_,
        out,
        time_limit.replace('\n', '').replace('\r', ''),
        "{",
        "}"
    )
    print("Adding simple test #{0} to db".format(i))
    db_insert("simple.{0}".format(i), "Testcases", simple_test_entry)

for i in range(1, nsystem + 1):
    in_ = read_and_get(os.path.join(question_folder,
                                    "system", "{0}.in".format(i)))
    out = read_and_get(os.path.join(question_folder,
                                    "system", "{0}.out".format(i)))
    system_test_entry = """
    {4}
        "problem_id": "{0}", 
        "input_data": `{1}`,
        "output_data": `{2}`,
        "time_limit": "{3}"
    {5}
    """.format(
        problem_id,
        in_,
        out,
        time_limit.replace('\n', '').replace('\r', ''),
        "{",
        "}"
    )
    print("Adding system test #{0} to db".format(i))
    db_insert("system.{0}".format(i), "SystemTests", simple_test_entry)

print("[DONE]")
