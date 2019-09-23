import subprocess

while True:
    try:
        print(subprocess.check_output(['python3.6', 'src/bot.py']))
    except KeyboardInterrupt:
        break
    except:
        pass

print("bot stopped running.")