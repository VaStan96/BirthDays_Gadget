import github


def checkNewVer():
    with open('.\Data\Version.txt', mode='r') as file:
        lines = file.readlines()
        currentVer = float(lines[1].split(' ')[1])

    g = github.Github()

    # Получите доступ к репозиторию, указав владельца и имя репозитория
    repo = g.get_repo('VaStan96/BirthDays_Gadget')
    # Получите последний коммит
    latest_commit = repo.get_commits()[0]
    # Получите сообщение последнего коммита
    commit_message = latest_commit.commit.message
    # Получите версию из сообщения последнего коммита
    gitVer = float(commit_message[commit_message.rfind('V')+1:])

    if currentVer < gitVer:
        return True
    else:
        return False

# if __name__ == '__main__':
#     print(checkNewVer())