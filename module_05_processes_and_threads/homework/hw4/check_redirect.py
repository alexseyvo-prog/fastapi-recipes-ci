from redirect import Redirect

print("Hello stdout")  # обычный вывод

stdout_file = open("stdout.txt", "w", encoding="utf-8")
stderr_file = open("stderr.txt", "w", encoding="utf-8")

with Redirect(stdout=stdout_file, stderr=stderr_file):
    print("Hello stdout.txt")
    raise Exception("Hello stderr.txt")

print("Hello stdout again")
raise Exception("Hello stderr")