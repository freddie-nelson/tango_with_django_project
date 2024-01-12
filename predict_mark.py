import os
import subprocess
import re

subprocess.getoutput("git branch -d test")
subprocess.getoutput("git checkout main")

git_log_output = subprocess.getoutput("git log --oneline")
commits = [{ "id": c.split(" ")[0], "message": " ".join(c.split(" ")[1:]) } for c in git_log_output.split("\n")]

tests_module = "tests"
tests = [f"tests_chapter{i}" for i in range(3, 11)]

total_tests_passed = 0
total_tests_ran = 0

for test in tests:
    test_command = f"python manage.py test {tests_module}.{test}"

    tests_failed = 1000000 
    tests_passed = 1000000

    for c in commits:
        print("Running test", os.path.basename(test), "on commit", c["id"], ":", c["message"])

        subprocess.getoutput(f"git branch -d test")
        subprocess.getoutput(f"git checkout -b test")
        subprocess.getoutput(f"git reset --hard {c['id']}")

        test_output = subprocess.getoutput(test_command)

        num_ran = int(re.search(r"Ran (\d+) tests", test_output).group(1))

        num_failed_re = re.search(r"FAILED \(failures=(\d+)\)", test_output)
        if num_failed_re:
            num_failed = int(num_failed_re.group(1))
        else:
            num_failed = 0

        if num_failed < tests_failed:
            tests_failed = num_failed
            tests_passed = num_ran - tests_failed

        print("Tests ran:", num_ran)
        print("Tests failed:", num_failed)

        if "OK" in test_output:
            print("Test passed on commit", c["id"], ":", c["message"])
            break

    total_tests_ran += tests_passed + tests_failed
    total_tests_passed += tests_passed

    print("Total tests passed:", total_tests_passed)
    print("Total tests ran:", total_tests_ran)


# delete test branch
print("Deleting test branch")
subprocess.getoutput("git checkout main")
subprocess.getoutput("git branch -d test")
        
# Reset to latest commit
# print("Resetting to latest commit")
# subprocess.getoutput(f"git reset --hard {commits[0]['id']}")  

print("Tests passed:", total_tests_passed)
print("Tests ran:", total_tests_ran)

print("Mark:", (total_tests_passed / total_tests_ran) * 100 * (min(len(commits), 8) / 8))
